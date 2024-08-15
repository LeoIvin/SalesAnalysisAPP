from django.shortcuts import render
from django.http import HttpResponse
from rest_framework.response import Response
from rest_framework.decorators import api_view
from rest_framework import status
from .forms import SalesDataForm
from .models import SalesData
from .utils.analysis import process_sales_csv, sales_by_month_analysis, top_selling_products_analysis

@api_view(['POST'])
def api_upload_sales_data(request):
    form = SalesDataForm(request.POST, request.FILES)
    if form.is_valid():
        sales_data = form.save()
        try:
            # Process the uploaded CSV file
            processed_df, summary = process_sales_csv(sales_data.file.path)

            # Perform analyses
            sales_by_month, summary_message_month, _ = sales_by_month_analysis(sales_data.file.path)
            top_selling_products, summary_message_products, _ = top_selling_products_analysis(sales_data.file.path)

            # Prepare response data
            response_data = {
                'summary': summary,
                'sales_by_month': sales_by_month.to_dict(),  # Convert Series to dictionary
                'top_selling_products': top_selling_products.to_dict(),  # Convert Series to dictionary
                'summary_message_month': summary_message_month,
                'summary_message_products': summary_message_products,
            }

            return Response(response_data, status=status.HTTP_200_OK)
        except ValueError as e:
            # Handle processing errors
            return Response({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
    return Response({'error': 'Invalid form data'}, status=status.HTTP_400_BAD_REQUEST)
