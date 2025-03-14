# WMS Assignment - Rohit Jain

## How to Use
1. Visit: [http://invincible123.pythonanywhere.com](http://invincible123.pythonanywhere.com)
2. Upload Flipkart and Amazon CSVs, click "Process Data".
3. Download the cleaned data as `cleaned_sales_data.csv`.

## What I Built
- **Part 1: Data Cleaning and Management**
  - Developed a Python-based Flask web app for cleaning and mapping sales data.
  - Features:
    - **SKU to MSKU Mapping**: Maps SKUs to MSKUs using combo and single SKU mapping files.
    - **Combo Product Handling**: Supports combo SKUs with multiple MSKUs via the `explode` method.
    - **Format-Flexible Input Processing**: Handles Flipkart (`Ordered On`) and Amazon (`Date`) CSV formats.
    - **VLOOKUP Limitation Elimination**: Replaces manual lookups with automated Python logic.
  - **Data Structure Specifications**:
    - Input CSV fields: Varies by marketplace (e.g., `SKU`, `Quantity`, `Ordered On` for Flipkart; `MSKU`, `Quantity`, `Date` for Amazon).
    - Output CSV fields: `SKU`, `Quantity`, `Date`, `Marketplace`, `MSKU`.
    - Mapping files: `Combos_skus.csv` (Combo, SKU1, SKU2, ..., Status) and `mskus_with_sku.csv.csv` (sku, msku, panels).
    - Combo SKUs with multiple MSKUs supported.
    - Marketplace-specific SKU formats (e.g., `CSTE FK` for Flipkart, `CSTE AMAZON` for Amazon).
    - Status field indicates combos in mapping data.
  - **Implementation Guidelines**:
    - **Development Steps**:
      - Created `SKUMapper` class to handle mapping logic.
      - Implemented master mapping loader for combo and single SKU files.
      - Developed `map_sku` function for SKU identification and mapping.
      - Added combo product handling with `explode` and logging.
      - Built a flexible input processor for Flipkart and Amazon CSVs.
    - **Enhanced Features**:
      - SKU format validation via string stripping and logging.
      - Missing mapping error handling with warnings in logs.
      - Multi-marketplace format support (Flipkart and Amazon).
      - Mapping process logging to `mapping.log`.
  - **Part 3: Flask App**:
    - Hosted a Flask web app on PythonAnywhere for user interaction.
    - Functionality: Upload Flipkart and Amazon sales data CSVs, process them with `SKUMapper`, and download the cleaned output.

- **Note**: The Airtable dashboard and API integration (Part 2) are **not currently included** in this web app. The web app is designed solely for uploading Flipkart and Amazon sales data and generating cleaned sales data as a CSV output, satisfying the requirements of Part 1 listed above.

## Airtable Sample Dashboard
- A sample Airtable dashboard created using the cleaned data from Step 1 (Part 1) is available here:
  - **[Airtable Dashboard Link](https://airtable.com/invite/l?inviteId=inv3DOqSOiM57pRq1&inviteToken=14f2ba71b473590a3a412ae7da829cd3c2aa8aa07ef119dbc8da141b912262ef&utm_medium=email&utm_source=product_team&utm_content=transactional-alerts)**
- This dashboard demonstrates how the cleaned data can be visualized but is not part of the deployed Flask web app.

## Setup
- **Deployed**: [http://invincible123.pythonanywhere.com](http://invincible123.pythonanywhere.com)
- **Local Setup**:
  1. Install dependencies: `pip install flask pandas`
  2. Place `Combos_skus.csv` and `mskus_with_sku.csv.csv` in a `data/` subdirectory.
  3. Run: `python app.py`
  4. Access: `http://localhost:5000`

## Dashboard Screenshots
Below are screenshots of the sample Airtable dashboard created from the cleaned data (not part of the Flask app):

1. **Total Stock (TLCQ)**:
   - *[Insert screenshot here: e.g., total_stock_screenshot.png]*
   - Description: Shows the sum of stock levels from the cleaned inventory data.

2. **Sales by Marketplace**:
   - *[Insert screenshot here: e.g., sales_by_marketplace_screenshot.png]*
   - Description: Bar chart displaying sales quantities for Flipkart and Amazon

3. **Low Stock Items**:
   - *[Insert screenshot here: e.g., low_stock_screenshot.png]*

