from unicodedata import decimal
import pandas as pd
import os
# import plotly.express as px 
from decimal import Decimal, InvalidOperation, ROUND_HALF_UP
from datetime import datetime

def safe_decimal_convert(value):
    """
    Safely convert a value to Decimal, handling various numeric formats.
    """
    try:
        if pd.isna(value) or value is None:
            return Decimal('0')
        if isinstance(value, (int, float)):
            return Decimal(str(value)).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        if isinstance(value, str):
            # Remove any currency symbols and thousands separators
            cleaned = value.replace('$', '').replace(',', '').strip()
            return Decimal(cleaned).quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        if isinstance(value, Decimal):
            return value.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)
        return Decimal('0')
    except (InvalidOperation, ValueError, TypeError):
        return Decimal('0')

def parse_date(date_str):
    """
    Try multiple date formats to parse a date string.
    """
    if pd.isna(date_str):
        return None
        
    date_formats = [
        '%Y-%m-%d',
        '%d/%m/%Y',
        '%m/%d/%Y',
        '%d-%m-%Y',
        '%Y/%m/%d',
        '%d/%m/%y',
        '%y-%m-%d',
        '%m-%d-%y',
        '%d-%m-%y'
    ]
    
    if isinstance(date_str, (datetime, pd.Timestamp)):
        return date_str
        
    if isinstance(date_str, str):
        for fmt in date_formats:
            try:
                return pd.to_datetime(date_str, format=fmt)
            except:
                continue
                
    try:
        # Try pandas default parser as last resort
        return pd.to_datetime(date_str)
    except:
        return None

def process_sales_file(file):
    """
    Process sales data file with improved error handling and decimal conversion.
    """
    required_columns = ['Product', 'Price', 'Quantity', 'Date']
    
    COLUMN_MAPPING = {
        'Product': ['Product', 'Item', 'Goods'],
        'Quantity': ['Quantity', 'Qty', 'Amount'],
        'Price': ['Price', 'Cost', 'Unit Price'],
        'Date': ['Date', 'Order Date', 'Transaction Date'],
        'Total Sales': ['Total Sales', 'Revenue', 'Sales']
    }

    try:
        # Read data with proper error handling
        try:
            data = pd.read_csv(file)
        except UnicodeDecodeError:
            try:
                data = pd.read_excel(file)
            except Exception as e:
                raise ValueError(f"Unable to read file. Error: {str(e)}")

        # Clean and normalize column names
        data.columns = data.columns.str.strip().str.title()
        
        # Normalize column names using mapping
        normalized_cols = {}
        for standard_col, alternatives in COLUMN_MAPPING.items():
            for alt in alternatives:
                if alt in data.columns:
                    normalized_cols[alt] = standard_col
                    break
        
        data.rename(columns=normalized_cols, inplace=True)

        # Verify required columns
        missing_cols = [col for col in required_columns if col not in data.columns]
        if missing_cols:
            raise ValueError(f"Missing required columns: {', '.join(missing_cols)}")

        # Convert Date column with improved parsing
        data['Date'] = data['Date'].apply(parse_date)
        
        # Check if any dates were successfully parsed
        if data['Date'].isnull().all():
            raise ValueError("Could not parse any dates in the Date column")

        # Drop rows with invalid dates
        data = data.dropna(subset=['Date'])
        
        if len(data) == 0:
            raise ValueError("No valid data rows after parsing dates")

        # Convert numeric columns with proper decimal handling
        data['Price'] = data['Price'].apply(safe_decimal_convert)
        data['Quantity'] = pd.to_numeric(data['Quantity'], errors='coerce').fillna(0).astype(int)

        # Calculate or clean Total Sales
        if 'Total Sales' not in data.columns:
            data['Total Sales'] = data.apply(
                lambda row: safe_decimal_convert(float(row['Price']) * float(row['Quantity'])), 
                axis=1
            )
        else:
            data['Total Sales'] = data['Total Sales'].apply(safe_decimal_convert)

        # Extract year and month for grouping
        data['Month'] = data['Date'].dt.strftime('%Y-%m')

        # Calculate summary statistics with proper decimal handling
        total_sales = sum(data['Total Sales'], Decimal('0'))
        avg_price = total_sales / Decimal(str(len(data))) if len(data) > 0 else Decimal('0')
        
        summary = {
            'total_rows': int(len(data)),
            'total_sales': str(total_sales.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)),
            'start_date': data['Date'].min().strftime('%Y-%m-%d'),
            'end_date': data['Date'].max().strftime('%Y-%m-%d'),
            'average_price': str(avg_price.quantize(Decimal('.01'), rounding=ROUND_HALF_UP))
        }

        return data, summary

    except Exception as e:
        raise ValueError(f"Error processing sales file: {str(e)}")

def sales_by_month_analysis(file):
    """
    Analyze sales data by month with proper decimal handling and error checking.
    """
    try:
        # Process the file
        data, summary = process_sales_file(file)

        # Group by Month and calculate total sales
        sales_by_month = data.groupby('Month')['Total Sales'].agg(sum)
        sales_by_month = sales_by_month.sort_values(ascending=False)

        # Calculate average monthly sales with proper decimal handling
        total_sales = sum(sales_by_month.values, Decimal('0'))
        num_months = Decimal(str(len(sales_by_month)))
        avg_sales = total_sales / num_months if num_months > 0 else Decimal('0')
        avg_sales = avg_sales.quantize(Decimal('.01'), rounding=ROUND_HALF_UP)

        # Find best performing month
        best_month = sales_by_month.index[0]
        best_month_sales = safe_decimal_convert(sales_by_month.iloc[0])

        # Prepare the summary dictionary with proper decimal handling
        summary_month = {
            "avg_sales_by_month": str(avg_sales),
            "best_month": best_month,
            "best_month_sales": str(best_month_sales),
            "summary_message": f"Best selling month is: {best_month} with ${best_month_sales:,.2f} in sales",
        }

        # Convert numpy arrays to lists for JSON serialization
        fig_x = sales_by_month.index.tolist()
        fig_y = [float(safe_decimal_convert(x)) for x in sales_by_month.values]

        return sales_by_month, summary_month, fig_x, fig_y

    except Exception as e:
        error_msg = f"Error in sales_by_month_analysis: {str(e)}"
        return None, {"error": error_msg}, None, None

def top_selling_products_analysis(file):
    """ 
    Analyzes sales data to determine the top-selling products.
    """
    try:
        data, summary = process_sales_file(file)

        # Convert the 'Quantity' column to Decimal
        data['Quantity'] = data['Quantity'].apply(Decimal)

        # Group products by quantities sold
        top_selling_products = data.groupby('Product')['Quantity'].sum().sort_values(ascending=False)

        # Convert index to strings if necessary
        top_selling_products.index = top_selling_products.index.astype(str)

        # Prepare summary message
        best_selling_product = top_selling_products.idxmax()
        best_selling_quantity = top_selling_products.max()
        summary_message = f"Best selling product is: {best_selling_product} with {best_selling_quantity} in quantity"

        summary_product = {
            "highest_selling_product": best_selling_product,
            "best_selling_quantity": best_selling_quantity,
            "summary_message": summary_message,
        }

        fig_x = top_selling_products.index
        fig_y = top_selling_products.values

        return top_selling_products, summary_product, fig_x, fig_y

    except Exception as e:
        return None, {"error": str(e)}, None, None  # Return 4 values in error case

def top_selling_by_total_sales_analysis(file):
    """
    Which products are the most profitable? (based on total sales)
    """
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

        summary_sales = {
            "best_selling_product": best_selling_product,
            "highest_sale_recorded": best_selling_sales,
            "summary_message": summary_message,
        }

        fig_x = top_selling_by_total_sales.index
        fig_y = top_selling_by_total_sales.values
        
        return top_selling_by_total_sales, summary_sales, fig_x, fig_y

    except Exception as e:
        return None, {"error": str(e)}, None, None  # Return 4 values in error case

def sales_trends_analysis(file):
    """
    Analyzes sales data to determine how sales trends vary throughout the year.
    """
    try:
        # Get sales by month data
        sales_by_month, summary_month, fig_x, fig_y = sales_by_month_analysis(file)
        if sales_by_month is None:
            raise ValueError("sales_by_month_analysis returned None")

        # Calculate the month-over-month percentage change in sales
        sales_by_month = sales_by_month.sort_index()  # Ensure the index is sorted by month
        sales_by_month_pct_change = sales_by_month.pct_change().dropna()

        # Define a threshold for significant changes (e.g., 20%)
        threshold = 0.20
        significant_changes = sales_by_month_pct_change[sales_by_month_pct_change.abs() > threshold]

        # Prepare summary message
        summary_message = ""
        if not significant_changes.empty:
            significant_months = significant_changes.index.tolist()
            summary_message = f"Significant changes in sales were observed in the following months: {', '.join(significant_months)}"
        else:
            summary_message = "No significant changes in sales were observed."

        fig_x = significant_changes.index
        fig_y = sales_by_month[significant_changes.index]

        return sales_by_month, {"summary_message": summary_message}, fig_x, fig_y

    except Exception as e:
        return None, {"error": str(e)}, None, None  # Return 4 values in error case