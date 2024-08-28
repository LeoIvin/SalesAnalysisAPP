from django.shortcuts import render
from django.http import HttpResponse
from .forms import SalesDataForm
from .utils.analysis import (process_sales_file, sales_by_month_analysis, 
                             top_selling_products_analysis, top_selling_by_total_sales_analysis, sales_trends_analysis)

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.exceptions import NotAuthenticated, AuthenticationFailed
from django.contrib.auth.decorators import login_required

@login_required(login_url='login')  
@api_view(['POST', 'GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
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
                
                # Additional Metrics 
                

                # Convert figures to JSON format for rendering in templates
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
                    # "fig_trends": fig_trends.to_json()
                }
                
                return render(request, 'dashboard.html', context)
            except ValueError as e:
                # Handle known errors in processing
                return HttpResponse(f"Error: {str(e)}", status=400)
            except Exception as e:
                # Handle unexpected errors
                return HttpResponse(f"An unexpected error occurred: {str(e)}", status=500)
    else:
        form = SalesDataForm()

    return render(request, 'upload_sales.html', {'form': form})


@login_required(login_url='login')  
@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def dashboard_view(request):
        if request.method == "GET":
            return render(request, 'dashboard.html')
        

def notFoundView(request):
    pass





            # Additional Metrics
            #    # Convert to appropriate types
            #     revenue = float(summary.get('total_sales', 0))
            #     best_selling_product = summary_products.get('best_selling_product', '')
            #     max_quantity_sold = int(summary_products.get('best_selling_quantity', 0))
            #     average_sales_per_month = float(summary_month.get('average_sales_per_month', 0))
            #     top_month_sales = summary_month.get('best_month', '0000-00')  # String format

            #     SalesSummary.objects.update_or_create(
            #         sales_data=sales_data, defaults={
            #             "revenue": revenue,
            #             "best_selling_product": best_selling_product,
            #             "max_quantity_sold": max_quantity_sold,
            #             "average_sales_per_month": average_sales_per_month,
            #             # "top_month_sales": top_month_sales
            #         }
            #     )