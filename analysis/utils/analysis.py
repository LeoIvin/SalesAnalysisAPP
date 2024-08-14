import pandas as pd
import numpy as np
import plotly.graph_objects as go
import plotly.express as px
import matplotlib.pyplot as plt


required_columns = ['Product', 'Price', 'Quantity', 'Date']

def process_sales_csv(file):
    # Read data
    try:
        data = pd.read_csv(file)
    except Exception as e:
        raise ValueError(f"Error reading data: {e}")
    
    # Ensure column names are consistent
    data.columns = data.columns.str.strip()  # Remove leading/trailing whitespace
    data.columns = data.columns.str.title()  # Standardize case

    # Debug: Print cleaned column names
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
        raise ValueError("Some dates could not be parsed. Please check the date format in the CSV.")
    
    # Calculate total sales
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
    data, summary = process_sales_csv(file)

    # Group by 'Month' and calculate total sales
    sales_by_month = data.groupby('Month')['Total Sales'].sum()
    sales_by_month = sales_by_month.sort_values(ascending=False)

    # Prepare summary message
    best_month = sales_by_month.idxmax()
    best_month_sales = sales_by_month.max()
    summary_message = f"Best selling month is: {best_month} with ${best_month_sales:.2f} in sales"

    # plot sales by month
    fig = px.bar(sales_by_month, x=sales_by_month.index.astype(str), y=sales_by_month.values, 
                 labels={"x":"Month", "y": "Total Sales"},  title='Total Sales by Month')
    fig.show()

    return sales_by_month, summary_message
