from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from analysis.views import upload_sales_data, DashboardView, notFoundView
from django.urls import re_path
from accounts.views import signup, login, test_token, login_view, signup_view, root, ProfileUpdateView, ProfileView


urlpatterns = [
    path("__reload__/", include("django_browser_reload.urls")),
    path("admin/", admin.site.urls),

    # API Endpoints
    path('api/login/', login, name='login_api'),
    path('api/signup/', signup, name='signup_api'),
    path('test_token/', test_token, name='test_token'),
    path('', root, name='root'),

    # Analysis Views
    path('upload/', upload_sales_data, name="upload_sales"),

    # Template Views
    path('login/', login_view, name='login'),
    path('signup/', signup_view, name='signup'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/update/', ProfileUpdateView.as_view(), name='update_profile'),
    path('dashboard/', DashboardView.as_view(), name='dashboard_view'),
    path('404/', notFoundView, name='404')
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

