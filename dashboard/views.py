from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
import requests

from analysis.views import upload_sales_data


def dashboard_view(request):
    token = request.session.get('auth_token')
    if not token:
        return redirect('login')

    # Example: Fetching user-specific data using the token
    headers = {'Authorization': f'Token {token}'}
    response = requests.get('http://127.0.0.1:8000/', headers=headers)

    if response.status_code == 200:
        data = response.json()
        return render(request, 'dashboard.html', {'data': data})
    else:
        messages.error(request, 'Failed to retrieve data.')
        return render(request, 'dashboard.html')

