from django.db import models
from django.contrib.auth.models import User
from django.contrib.postgres.fields import ArrayField
from datetime import date

class SalesData(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    file = models.FileField(upload_to='sales_data/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Sales Data - {self.uploaded_at.strftime('%Y-%m-%d %H:%M')}"

class SalesSummary(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True)
    sales_data = models.OneToOneField(
        SalesData, 
        on_delete=models.CASCADE, 
        related_name='summary'
    )
    created_at = models.DateTimeField(auto_now_add=True, null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)

    # General Summary
    total_rows = models.IntegerField(
        default=0
    )
    total_sales = models.FloatField(
        default=0.00
    )
    start_date = models.DateField(
        default=date.today
    )
    end_date = models.DateField(
        default=date.today
    )

    # Monthly Summary
    best_month = models.CharField(
        max_length=20, 
        default=''
    )
    avg_sales_by_month = models.FloatField(
        default=0.00
    )
    sales_by_month_x = ArrayField(
        models.CharField(max_length=20), 
        null=True, 
        blank=True,
        default=list
    )
    sales_by_month_y = ArrayField(
        models.DecimalField(max_digits=15, decimal_places=2), 
        null=True, 
        blank=True,
        default=list
    )

    # Product Summary
    best_selling_product = models.CharField(
        max_length=255, 
        default=''
    )
    highest_quantity_sold = models.IntegerField(
        default=0
    )
    product_sales_x = ArrayField(
        models.CharField(max_length=255), 
        null=True, 
        blank=True,
        default=list
    )
    product_sales_y = ArrayField(
        models.DecimalField(max_digits=15, decimal_places=2), 
        null=True, 
        blank=True,
        default=list
    )

    # Sales Analysis
    highest_sale_recorded = models.FloatField(
        default=0.00
    )
    total_sales_x = ArrayField(
        models.CharField(max_length=255), 
        null=True, 
        blank=True,
        default=list
    )
    total_sales_y = ArrayField(
        models.DecimalField(max_digits=15, decimal_places=2), 
        null=True, 
        blank=True,
        default=list
    )

    # Trends
    significant_changes = models.TextField(
        null=True, 
        blank=True,
        default=''
    )

    class Meta:
        verbose_name_plural = "Sales Summaries"

    def __str__(self):
        return f"Summary for {self.sales_data}"