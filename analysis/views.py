from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.views import View
from .utils.analysis import process_sales_file, sales_by_month_analysis, top_selling_products_analysis
import pandas as pd
import io

@csrf_exempt
def upload_sales_data(request):
    if request.method == "POST":
        file = request.FILES.get('file')
        if file:
            try:
                if file.name.endswith('.csv'):
                    processed_df, summary = process_sales_file(file)
                elif file.name.endswith('.xlsx'):
                    df = pd.read_excel(file)
                    file = io.StringIO(df.to_csv(index=False))
                    processed_df, summary = process_sales_file(file)
                else:
                    return JsonResponse({'error': 'Unsupported file format'}, status=400)

                # Perform analysis
                sales_by_month, summary_message_month, _ = sales_by_month_analysis(file)
                top_selling_products, summary_message_products, _ = top_selling_products_analysis(file)

                response_data = {
                    'summary': summary,
                    'sales_by_month': sales_by_month.to_dict(),
                    'top_selling_products': top_selling_products.to_dict()
                }

                return JsonResponse(response_data)
            except ValueError as e:
                return JsonResponse({'error': str(e)}, status=400)
        else:
            return JsonResponse({'error': 'No file uploaded'}, status=400)
    return JsonResponse({'error': 'Invalid request method'}, status=405)
