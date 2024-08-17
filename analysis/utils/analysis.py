import pandas as pd
import os
import plotly.express as px 


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
    # Read data
    try:
        data = pd.read_csv(file)
    except UnicodeDecodeError as e:
        try:
            data = pd.read_excel(file)
        except Exception as e:
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
        data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%y', errors='coerce')
    except Exception as e:
        raise ValueError(f"Error converting Date column to datetime: {e}")
    
    # Drop rows with NaN in the Date column
    # data = data.dropna(subset=['Date'])

    # Ensure no operations are performed on NaT values
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
    Analyzes sales data to determine which months have the highest sales.

    Parameters:
    file (str): Path to the sales data file.

    Returns:
    tuple: A tuple containing the sales by month DataFrame, a summary message, and the plotly figure.
    """
    try:
        data, summary = process_sales_file(file)

        # Group by 'Month' and calculate total sales
        sales_by_month = data.groupby('Month')['Total Sales'].sum().sort_values(ascending=False)

        # Convert Period objects to strings
        sales_by_month.index = sales_by_month.index.astype(str)

        # Prepare summary message
        best_month = sales_by_month.idxmax()
        best_month_sales = sales_by_month.max()
        summary_message = f"Best selling month is: {best_month} with ${best_month_sales:.2f} in sales"

        # Create bar plot
        fig = px.line(x=sales_by_month.index, y=sales_by_month.values,
                     labels={"x": "Month", "y": "Total Sales"})

        return sales_by_month, summary_message, fig

    except Exception as e:
        return None, f"An error occurred: {e}", None


def top_selling_products_analysis(file):
    """ 
    Analyzes sales data to determine the top-selling products.

    Parameters:
    file (str): Path to the sales data file.

    Returns:
    tuple: A tuple containing the top-selling products DataFrame, a summary message, and the plotly figure.
    """
    try:
        data, summary = process_sales_file(file)

        # Group products by quantities sold
        top_selling_products = data.groupby('Product')['Quantity'].sum().sort_values(ascending=False)

        # Convert index to strings if necessary
        top_selling_products.index = top_selling_products.index.astype(str)

        # Prepare summary message
        best_selling_product = top_selling_products.idxmax()
        best_selling_quantity = top_selling_products.max()
        summary_message = f"Best selling product is: {best_selling_product} with {best_selling_quantity:.2f} in quantity"

        fig = px.line(x=top_selling_products.index, y=top_selling_products.values, 
                     labels={"x": "Products", "y": "Quantity"})

        return top_selling_products, summary_message, fig
    except Exception as e:
        return None, f"An error occurred: {e}"
    

def top_selling_by_total_sales_analysis(file):

    try:
        data, summary = process_sales_file(file)

        # group products by total sales
        top_selling_by_total_sales = data.groupby('Product')['Total Sales'].sum().sort_values(ascending=False)

        # Convert index to strings if necessary
        top_selling_by_total_sales.index = top_selling_by_total_sales.index.astype(str)

        # Prepare summary message
        best_selling_product = top_selling_by_total_sales.idxmax()
        best_selling_sales = top_selling_by_total_sales.max()
        summary_message = f"Best selling product is {best_selling_product} with {best_selling_sales} total sales."

        # plot results
        fig = px.line(x=top_selling_by_total_sales.index, y=top_selling_by_total_sales.values,
                      labels={'x': 'Product', 'y': 'Total Sales'})
        
        return top_selling_by_total_sales, summary_message, fig
    except Exception as e:
        return None, f"An error occured {e}"