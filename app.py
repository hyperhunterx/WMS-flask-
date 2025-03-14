from flask import Flask, request, render_template, send_file
import pandas as pd
import logging
import os

# Configure logging
logging.basicConfig(filename='mapping.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class SKUMapper:
    def __init__(self, combo_file, single_sku_file=None, combo_col='Combo', status_col='Status'):
        # Load combo mappings
        df = pd.read_csv(combo_file, skipinitialspace=True)
        available_cols = [col.strip() for col in df.columns]
        if combo_col not in available_cols:
            raise ValueError(f"Combo column '{combo_col}' not found in {combo_file}")
        sku_cols = [col for col in available_cols if col.startswith('SKU') and col[3:].isdigit()]
        usecols = [combo_col] + sku_cols + ([status_col] if status_col in available_cols else [])
        self.combos = pd.read_csv(combo_file, usecols=usecols, skipinitialspace=True)
        if status_col in self.combos.columns:
            self.combos = self.combos[self.combos[status_col].str.contains('Combo', na=False)]
        self.combos = self.combos.dropna(subset=[combo_col])
        self.mappings = self.combos.melt(id_vars=[combo_col], value_vars=sku_cols,
                                         var_name='SKU_Num', value_name='MSKU').dropna(subset=['MSKU'])
        self.mappings = self.mappings[[combo_col, 'MSKU']]
        self.combo_col = combo_col

        # Load single SKU mappings
        self.single_mappings = None
        if single_sku_file:
            self.single_mappings = pd.read_csv(single_sku_file, usecols=['sku', 'msku', 'panels'])
            self.single_mappings = self.single_mappings.dropna(subset=['sku', 'msku'])
            self.single_mappings['sku'] = self.single_mappings['sku'].str.strip()
            self.single_mappings['msku'] = self.single_mappings['msku'].str.strip()
            logging.info(f"Loaded {len(self.single_mappings)} single SKU mappings from {single_sku_file}")

    def map_sku(self, sku, marketplace=None):
        sku = str(sku).strip()
        combo_match = self.mappings[self.mappings[self.combo_col] == sku]
        if not combo_match.empty:
            mskus = combo_match['MSKU'].tolist()
            logging.info(f"Combo SKU {sku} mapped to MSKUs: {mskus} for marketplace: {marketplace}")
            return mskus
        
        if self.single_mappings is not None:
            if marketplace == 'Flipkart':
                marketplace_filter = 'CSTE FK'
            elif marketplace == 'Amazon':
                marketplace_filter = 'CSTE AMAZON'
            else:
                marketplace_filter = None
            
            single_match = self.single_mappings[self.single_mappings['sku'] == sku]
            if marketplace_filter:
                single_match = single_match[single_match['panels'] == marketplace_filter]
            
            if not single_match.empty:
                msku = single_match['msku'].iloc[0]
                logging.info(f"Single SKU {sku} mapped to MSKU: {msku} for marketplace: {marketplace}")
                return [msku]

        logging.warning(f"No mapping for SKU: {sku} in {marketplace}, assuming single MSKU")
        return [sku]

    def process_flipkart(self, flipkart_file):
        data = pd.read_csv(flipkart_file)
        data = data[data['Order State'].isin(['Delivered', 'Shipped'])]
        flipkart_data = data[['SKU', 'Quantity', 'Ordered On']].copy()
        flipkart_data['Marketplace'] = 'Flipkart'
        flipkart_data.columns = ['SKU', 'Quantity', 'Date', 'Marketplace']
        return flipkart_data

    def process_amazon(self, amazon_file):
        data = pd.read_csv(amazon_file)
        data = data[data['Event Type'] == 'Shipments']
        data['Quantity'] = data['Quantity'].abs()
        amazon_data = data[['MSKU', 'Quantity', 'Date']].copy()
        amazon_data['Marketplace'] = 'Amazon'
        amazon_data.columns = ['SKU', 'Quantity', 'Date', 'Marketplace']
        return amazon_data

    def process_sales_data(self, flipkart_file, amazon_file, output_file='cleaned_sales_data.csv', split_quantity=False):
        flipkart_data = self.process_flipkart(flipkart_file)
        amazon_data = self.process_amazon(amazon_file)
        combined_data = pd.concat([flipkart_data, amazon_data], ignore_index=True)
        combined_data['MSKU'] = combined_data.apply(lambda row: self.map_sku(row['SKU'], row['Marketplace']), axis=1)

        exploded_data = combined_data.explode('MSKU').dropna(subset=['MSKU'])
        if split_quantity:
            exploded_data['Combo_Count'] = exploded_data.groupby(level=0)['MSKU'].transform('count')
            exploded_data['Quantity'] = exploded_data['Quantity'] / exploded_data['Combo_Count']
            exploded_data = exploded_data.drop(columns=['Combo_Count'])

        exploded_data['Date'] = pd.to_datetime(exploded_data['Date'], errors='coerce').dt.strftime('%Y-%m-%d')
        exploded_data.to_csv(output_file, index=False)
        logging.info(f"Processed {len(combined_data)} rows, expanded to {len(exploded_data)} rows with MSKUs")
        return exploded_data

# Initialize Flask app
app = Flask(__name__)

# Load SKUMapper with mapping files in 'data/' subdirectory
mapper = SKUMapper('data/Combos_skus.csv', single_sku_file='data/mskus_with_sku.csv.csv')

@app.route('/', methods=['GET', 'POST'])
def index():
    message = None
    download_available = False
    output_path = 'cleaned_sales_data.csv'

    if request.method == 'POST':
        if 'flipkart_file' not in request.files or 'amazon_file' not in request.files:
            message = 'Please upload both Flipkart and Amazon CSV files'
        else:
            flipkart_file = request.files['flipkart_file']
            amazon_file = request.files['amazon_file']
            if flipkart_file.filename == '' or amazon_file.filename == '':
                message = 'One or both files are missing'
            else:
                # Save uploaded files temporarily
                flipkart_path = 'uploaded_flipkart.csv'
                amazon_path = 'uploaded_amazon.csv'
                flipkart_file.save(flipkart_path)
                amazon_file.save(amazon_path)

                # Process with SKUMapper
                try:
                    mapper.process_sales_data(flipkart_path, amazon_path, output_file=output_path)
                    message = 'Data processed successfully!'
                    download_available = True
                except Exception as e:
                    message = f'Error processing data: {str(e)}'

                # Clean up temporary files
                if os.path.exists(flipkart_path):
                    os.remove(flipkart_path)
                if os.path.exists(amazon_path):
                    os.remove(amazon_path)

    return render_template('index.html', message=message, download_available=download_available)

@app.route('/download')
def download_file():
    return send_file('cleaned_sales_data.csv', as_attachment=True, download_name='cleaned_sales_data.csv')

if __name__ == "__main__":
    app.run(debug=True)