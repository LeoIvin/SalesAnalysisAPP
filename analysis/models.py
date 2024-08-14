from django.db import models

class SalesData(models.Model):
    file = models.FileField(upload_to='sales_data/')
    uploaded_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"File uploaded at {self.uploaded_at}"
