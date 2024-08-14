import pandas as pd
import numpy as np
# from plotly.graph_objects import Figure, show
import matplotlib.pyplot as plt
# import tensorflow as tf


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
        data['Date'] = pd.to_datetime(data['Date'], format='%d/%m/%y', errors='coerce', dayfirst=True)
        if data['Date'].isnull().any():
            raise ValueError("Date column has invalid date formats that could not be parsed.")
    except Exception as e:
        raise ValueError(f"Error converting Date column to datetime: {e}")
    
    # Calculate total sales for each entry
    data['Total Sales'] = data['Quantity'] * data['Price']

    # Create summary
    summary = {
        'total_rows': len(data),
        'total_sales': data['Total Sales'].sum(),
        'start_date': data['Date'].min(),
        'end_date': data['Date'].max()
    }

    return data, summary