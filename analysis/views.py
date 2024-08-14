from django.shortcuts import render, redirect
from django.http import HttpResponse
from .forms import SalesDataForm
from .models import SalesData
from .utils.analysis import process_sales_csv, sales_by_month_analysis

def upload_sales_data(request):
    if request.method == 'POST':
        form = SalesDataForm(request.POST, request.FILES)
        if form.is_valid():
            sales_data = form.save()
            try:
                # Process the uploaded CSV file
                processed_df, summary = process_sales_csv(sales_data.file.path)
                
                 # Perform sales by month analysis
                sales_by_month, summary_message = sales_by_month_analysis(sales_data.file.path)

                # Prepare context for rendering the template
                context = {
                    'summary': summary,
                    'sales_by_month': sales_by_month.to_dict(),  # Convert Series to dictionary for easier template use
                    'summary_message': summary_message,
                }
                
                return render(request, 'upload_success.html', context)
            except ValueError as e:
                # Handle any errors in processing
                return HttpResponse(f"Error: {str(e)}", status=400)
    else:
        form = SalesDataForm()

    return render(request, 'upload_sales.html', {'form': form})
