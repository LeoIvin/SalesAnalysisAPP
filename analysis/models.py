from django.db import models

class SalesData(models.Model):
    file = models.FileField(upload_to='sales_data/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File uploaded at {self.uploaded_at}"
    
class SalesSummary(models.Model):
    sales_data = models.OneToOneField(SalesData, on_delete=models.CASCADE)
    revenue = models.FloatField()  # Changed from CharField to FloatField
    best_selling_product = models.CharField(max_length=255)
    max_quantity_sold = models.IntegerField()  # Changed from CharField to IntegerField
    average_sales_per_month = models.FloatField()  # Changed from CharField to FloatField
    # top_month_sales = models.CharField(max_length=7)  # Keep this as a CharField to store dates like "2024-07" 
