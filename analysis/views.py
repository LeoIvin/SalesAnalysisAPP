# views.py

from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import SalesDataForm
from .models import SalesData
from .utils.analysis import process_sales_csv  

def upload_sales_data(request):
    if request.method == 'POST':
        form = SalesDataForm(request.POST, request.FILES)
        if form.is_valid():
            sales_data = form.save()
            try:
                # Process the uploaded CSV file
                processed_df, summary = process_sales_csv(sales_data.file.path)
                # You can add logic to save the processed data or display it
                return render(request, 'upload_success.html', {'summary': summary})
            except ValueError as e:
                # Handle any errors in processing
                return HttpResponse(f"Error: {str(e)}", status=400)
    else:
        form = SalesDataForm()

    return render(request, 'upload_sales.html', {'form': form})
