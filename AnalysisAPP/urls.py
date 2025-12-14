from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.urls import re_path
from accounts.views import signup, login, test_token, ProfileUpdateView, ProfileView
from dashboard.views import DashboardView
from analysis.views import upload_sales_data, get_sales_summary
from django.http import HttpResponse

def home(request):
    return HttpResponse("Welcome to AnalysisAPP!")



urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),
    path("admin/", admin.site.urls),
    path('', home, name='home'),

    
    # Authentication & Profile Endpoints
    path('api/login/', login, name='login_api'),
    path('api/signup/', signup, name='signup_api'),
    path('test_token/', test_token, name='test_token'),
    path('profile/update/', ProfileUpdateView.as_view(), name='update_profile'),
    path('profile/', ProfileView.as_view(), name='profile'),

    # Analysis & Dashboard Endpoints
    path('api/summary/', get_sales_summary, name='get_latest_summary'),
    path('api/summary/<int:summary_id>/', get_sales_summary, name='get_summary'),
    path('upload/', upload_sales_data, name='upload_sales'),
    path('dashboard/', DashboardView.as_view(), name='dashboard_view'),

    # Billing
    # path('payments/')
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
