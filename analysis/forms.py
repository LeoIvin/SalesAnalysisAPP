from django import forms 
from .models import SalesData

class SalesDataForm(forms.ModelForm):
    class Meta:
        model = SalesData
        fields = ['file']