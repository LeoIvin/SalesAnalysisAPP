from django.shortcuts import render, redirect
from django.urls import reverse
from django.contrib import messages
import requests
from django.contrib.auth.decorators import login_required



@login_required(login_url='login')  # Redirect to login if the user is not authenticated
def dashboard_view(request):

    user = request.user
    data = {
        'username': user.username,
        'email': user.email,
        # Add any other user-specific data
    }

    token = request.session.get('auth_token')
    if not token:
        return redirect('login')

    headers = {'Authorization': f'Token {token}'}
    response = requests.get('http://127.0.0.1:8000/user-data/', headers=headers)

    if response.status_code == 200:
        data = response.json()
        return render(request, 'dashboard.html', {'data': data})
    else:
        messages.error(request, 'Failed to retrieve data.')
        return render(request, 'dashboard.html')


