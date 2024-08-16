import pandas as pd
import os

required_columns = ['Product', 'Price', 'Quantity', 'Date']

COLUMN_MAPPING = {
    'Product': ['Product', 'Item', 'Goods'],
    'Quantity': ['Quantity', 'Qty', 'Amount'],
    'Price': ['Price', 'Cost', 'Unit Price'],
    'Date': ['Date', 'Order Date', 'Transaction Date'],
    'Total Sales': ['Total Sales', 'Revenue', 'Sales']
}

def normalize_columns(data, column_mapping):
    normalized_columns = {}
    for standard_col, alternatives in column_mapping.items():
        for alt in alternatives:
            if alt in data.columns:
                normalized_columns[standard_col] = alt
                break
    return normalized_columns

def process_sales_file(file):
   # Determine file extension
    file_extension = os.path.splitext(file)[1].lower()

    # Try reading the file based on the file extension
    try:
        if file_extension == '.csv':
            data = pd.read_csv(file)
        elif file_extension == '.xls':
            data = pd.read_excel(file, engine='xlrd')
        elif file_extension == '.xlsx':
            data = pd.read_excel(file, engine='openpyxl')
        else:
            raise ValueError(f"Unsupported file format: {file_extension}")
    except Exception as e:
        # If reading fails, attempt to use xlrd for `.xls` files
        if file_extension == '.xls':
            try:
                import xlrd
                # Fallback to xlrd
                data = pd.read_excel(file, engine='xlrd')
            except Exception as fallback_e:
                raise ValueError(f"Error reading data with xlrd: {fallback_e}")
        else:
            raise ValueError(f"Error reading data: {e}")
    # Ensure column names are consistent
    data.columns = data.columns.str.strip()  # Remove leading/trailing whitespace
    data.columns = data.columns.str.title()  # Standardize case

    # Normalize column names
    normalized_cols = normalize_columns(data, COLUMN_MAPPING)
    data.rename(columns=normalized_cols, inplace=True)
    
    # Print the cleaned column names for debugging purposes
    print(f"Cleaned column names: {data.columns.tolist()}")

    # Check for missing required columns
    missing = [column for column in required_columns if column not in data.columns]
    if missing:
        raise ValueError(f"File missing one or more required columns: {', '.join(missing)}")
    
    # Convert Date column to datetime format
    try:
        data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%y', errors='coerce')  # Adjust format if needed
    except Exception as e:
        raise ValueError(f"Error converting Date column to datetime: {e}")
    
    # Handle any dates that could not be parsed
    if data['Date'].isnull().any():
        raise ValueError("Some dates could not be parsed. Please check the date format in the file.")
    
    # Calculate total sales
    if 'Total Sales' not in data.columns:
        data['Total Sales'] = data['Quantity'] * data['Price']
    
    # Add a 'Month' column for grouping
    data['Month'] = data['Date'].dt.to_period('M')

    # Summary
    summary = {
        'total_rows': len(data),
        'total_sales': data['Total Sales'].sum(),
        'start_date': data['Date'].min(),
        'end_date': data['Date'].max()
    }

    return data, summary

def sales_by_month_analysis(file):
    """
    **Which months have the highest sales?**
    """
    data, summary = process_sales_file(file)

    # Group by 'Month' and calculate total sales
    sales_by_month = data.groupby('Month')['Total Sales'].sum()
    sales_by_month = sales_by_month.sort_values(ascending=False)

    # Prepare summary message
    best_month = sales_by_month.idxmax()
    best_month_sales = sales_by_month.max()
    summary_message = f"Best selling month is: {best_month} with ${best_month_sales:.2f} in sales"

    return sales_by_month, summary_message

def top_selling_products_analysis(file):
    """ 
    **What are the top-selling products?**
    """
    data, summary = process_sales_file(file)

    # Group products by quantities sold
    top_selling_products = data.groupby('Product')['Quantity'].sum()
    top_selling_products = top_selling_products.sort_values(ascending=False)

    best_selling_product = top_selling_products.idxmax()
    best_selling_quantity = top_selling_products.max()
    summary_message = f"Best selling product is: {best_selling_product} with {best_selling_quantity:.2f} in quantity"

    return top_selling_products, summary_message
