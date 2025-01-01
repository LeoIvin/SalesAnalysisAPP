from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from analysis.models import SalesSummary
from dashboard.serializers import SalesSummarySerializer

class DashboardView(APIView):
    authentication_classes = [SessionAuthentication, TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        try:
            # Get the latest summary for the authenticated user
            summary = SalesSummary.objects.filter(
                user=request.user
            ).order_by('-created_at').first()

            if not summary:
                return Response(
                    {"message": "No sales summary found for this user"},
                    status=status.HTTP_404_NOT_FOUND
                )

            serializer = SalesSummarySerializer(summary)
            return Response(serializer.data)

        except Exception as e:
            return Response(
                {"error": str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )