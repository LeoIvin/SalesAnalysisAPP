from django.shortcuts import render
from django.http import HttpResponse
from .forms import SalesDataForm
from .utils.analysis import (process_sales_file, sales_by_month_analysis, 
                             top_selling_products_analysis, top_selling_by_total_sales_analysis, sales_trends_analysis)

def upload_sales_data(request):
    if request.method == 'POST':
        form = SalesDataForm(request.POST, request.FILES)
        if form.is_valid():
            sales_data = form.save()
            try:
                # Process the uploaded file
                processed_df, summary = process_sales_file(sales_data.file.path)

                # Perform sales by month analysis
                sales_by_month, summary_month, fig_month = sales_by_month_analysis(sales_data.file.path)

                # Perform top selling products by quantity analysis
                top_selling_products, summary_products, fig_products = top_selling_products_analysis(sales_data.file.path)

                # Perform top selling products by total sales analysis
                top_selling_sales, summary_sales, fig_sales = top_selling_by_total_sales_analysis(sales_data.file.path)

                # Perform sales trend analysis
                sales_trends, summary_trends, fig_trends = sales_trends_analysis(sales_data.file.path)

                # Check if the summary is populated correctly
                if not (summary and summary_month and summary_products and summary_sales and summary_trends):
                    raise ValueError("Summary data is missing or invalid.")
                
                context = {
                    'summary': summary,
                    'summary_month': summary_month,
                    "fig_month": fig_month.to_json(),
                    "summary_products": summary_products,
                    "fig_products": fig_products.to_json(),
                    "summary_sales": summary_sales,
                    "fig_sales": fig_sales.to_json(),
                    "sales_trends": sales_trends,
                    "summary_trends": summary_trends,
                    "fig_trends": fig_trends.to_json()
                }
                
                return render(request, 'upload_success.html', context)
            except ValueError as e:
                # Handle any errors in processing
                return HttpResponse(f"Error: {str(e)}", status=400)
            except Exception as e:
                # Handle any other unexpected errors
                return HttpResponse(f"An unexpected error occurred: {str(e)}", status=500)
    else:
        form = SalesDataForm()

    return render(request, 'upload_sales.html', {'form': form})