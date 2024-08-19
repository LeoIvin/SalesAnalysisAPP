from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from analysis.views import upload_sales_data
from django.urls import re_path
from accounts.views import signup, login, test_token


urlpatterns = [
    path('admin/', admin.site.urls),
    path('upload/', upload_sales_data, name='upload_sales'),
    path('__reload__/', include('django_browser_reload.urls')),  # Ensure correct path formatting
    path('login/', login),
    path('signup/', signup),
    path('test_token', test_token),
    path('api/login/', login, name='login_api'),
    path('api/signup/', signup, name='signup_api'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
