from django.shortcuts import render
from django.http import HttpResponse
from .forms import SalesDataForm
from .utils.analysis import process_sales_file, sales_by_month_analysis, top_selling_products_analysis

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

                # Check if the summary is populated correctly
                if not (summary and summary_month and summary_products):
                    raise ValueError("Summary data is missing or invalid.")
                
                context = {
                    'summary': summary,
                    'summary_month': summary_month,
                    "fig_month": fig_month.to_json(),
                    "summary_products": summary_products,
                    "fig_products": fig_products.to_json()
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