from rest_framework.serializers import ModelSerializer
from analysis.models import SalesSummary

class SalesSummarySerializer(ModelSerializer):
    class Meta:
        model = SalesSummary
        fields = '__all__'