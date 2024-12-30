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
from django.http import JsonResponse

from django.views.decorators.csrf import csrf_exempt

from django.contrib.auth.mixins import LoginRequiredMixin
from accounts.models import Profile
from django.shortcuts import get_object_or_404
from django.utils.decorators import method_decorator
from django.views import View

from .models import SalesData, SalesSummary



@api_view(['POST', 'GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def upload_sales_data(request):
    if request.method == 'POST':
        form = SalesDataForm(request.POST, request.FILES)
        if form.is_valid():
            # Save the sales data file and associate it with the user
            sales_data = form.save(commit=False)
            sales_data.user = request.user
            sales_data.save()

            try:
                # Process the uploaded file
                processed_df, summary = process_sales_file(sales_data.file.path)

                # Perform analyses
                analyses = [
                    sales_by_month_analysis(sales_data.file.path),
                    top_selling_products_analysis(sales_data.file.path),
                    top_selling_by_total_sales_analysis(sales_data.file.path),
                    sales_trends_analysis(sales_data.file.path)
                ]

                # Check for errors in any analysis
                for analysis_result in analyses:
                    if analysis_result[0] is None:
                        return Response({"error": analysis_result[1]["error"]}, status=400)

                # Unpack results after error checking
                sales_by_month, summary_month, fig_by_month_x, fig_by_month_y = analyses[0]
                top_selling_products, summary_products, fig_products_x, fig_products_y = analyses[1]
                top_selling_sales, summary_sales, fig_sales_x, fig_sales_y = analyses[2]
                sales_trends, summary_trends, fig_trends_x, fig_trends_y = analyses[3]

                # Create or update sales summary in database
                sales_summary = SalesSummary.objects.create(
                    sales_data=sales_data,
                    # General Summary
                    total_rows=summary['total_rows'],
                    total_sales=summary['total_sales'],
                    start_date=summary['start_date'],
                    end_date=summary['end_date'],
                    
                    # Monthly Summary
                    best_month=summary_month['best_month'],
                    avg_sales_by_month=summary_month['avg_sales_by_month'],
                    sales_by_month_x=list(fig_by_month_x),
                    sales_by_month_y=list(fig_by_month_y),
                    
                    # Product Summary
                    best_selling_product=summary_products['highest_selling_product'],
                    highest_quantity_sold=int(summary_products['best_selling_quantity']),
                    product_sales_x=list(fig_products_x),
                    product_sales_y=list(fig_products_y),
                    
                    # Sales Analysis
                    highest_sale_recorded=summary_sales['highest_sale_recorded'],
                    total_sales_x=list(fig_sales_x),
                    total_sales_y=list(fig_sales_y),
                    
                    # Trends
                    significant_changes=summary_trends.get('summary_message', '')
                )

                # Prepare response data
                data = {
                    'summary': summary,
                    'summary_month': summary_month,
                    "sales_by_month_x": [fig_by_month_x if fig_by_month_x is not None else None],
                    "sales_by_month_y": [fig_by_month_y if fig_by_month_y is not None else None],
                    "summary_products": summary_products,
                    "top_selling_products_x": [fig_products_x if fig_products_x is not None else None],
                    "top_selling_products_y": [fig_products_y if fig_products_y is not None else None],
                    "summary_sales": summary_sales,
                    "top_selling_by_total_sales_x": [fig_sales_x if fig_sales_x is not None else None],
                    "top_selling_by_total_sales_y": [fig_sales_y if fig_sales_y is not None else None],
                    "summary_trends": summary_trends,
                    "summary_id": sales_summary.id  # Include the ID of the saved summary
                }
                
                return Response(data, status=200)
            except Exception as e:
                # Delete the sales data if processing fails
                sales_data.delete()
                return Response({"error": str(e)}, status=500)
        else:
            return Response({"error": "Invalid form data"}, status=400)
    else:
        return Response({"error": "GET method not supported for file upload"}, status=405)

# Get sales summary
@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def get_sales_summary(request, summary_id):
    try:
        summary = SalesSummary.objects.get(id=summary_id, sales_data__user=request.user)
        data = {
            'total_rows': summary.total_rows,
            'total_sales': str(summary.total_sales),
            'start_date': summary.start_date,
            'end_date': summary.end_date,
            'best_month': summary.best_month,
            'avg_sales_by_month': str(summary.avg_sales_by_month),
            'best_selling_product': summary.best_selling_product,
            'highest_quantity_sold': summary.highest_quantity_sold,
            'highest_sale_recorded': str(summary.highest_sale_recorded),
            'significant_changes': summary.significant_changes,
            'sales_by_month_x': summary.sales_by_month_x,
            'sales_by_month_y': summary.sales_by_month_y,
            'product_sales_x': summary.product_sales_x,
            'product_sales_y': summary.product_sales_y,
            'total_sales_x':  summary.total_sales_x,
            'total_sales_y':  summary.total_sales_y
        }
        return Response(data)
    except SalesSummary.DoesNotExist:
        return Response({"error": "Summary not found"}, status=404)





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