from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import UserSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db import IntegrityError

from django.shortcuts import get_object_or_404
from django.shortcuts import render, redirect


from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

import requests
from django.urls import reverse

from django.contrib.auth import authenticate, login as auth_login



# DRF API Views
@api_view(["POST"])
def login(request):
    user = get_object_or_404(User, username=request.data['username'])
    if not user.check_password(request.data['password']):
        return Response("missing user", status=status.HTTP_404_NOT_FOUND)
    token, created = Token.objects.get_or_create(user=user)
    serializer = UserSerializer(user)
    return Response({"token": token.key, "user": serializer.data})


@api_view(["POST"])
def signup(request):
    serializer = UserSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        user = User.objects.get(username=request.data['username'])
        user.set_password(request.data['password'])
        user.save()
        token = Token.objects.create(user=user)
        return Response({"token": token.key, "user": serializer.data})
    return Response(serializer.error, status=status.HTTP_400_BAD_REQUEST)

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response(f"passed for {request.user.username}")


# Django Template Views
def login_view(request):
    if request.method == "POST":
        username = request.POST.get('username')
        password = request.POST.get('password')

        if not username or not password:
            return render(request, 'login.html', {'error': 'All fields are required'})

        user = authenticate(request, username=username, password=password)
        if user is not None:
            auth_login(request, user)  # Log the user in
            return redirect(reverse('upload_sales'))
        else:
            return render(request, 'login.html', {'error': 'Invalid username or password'})

    return render(request, 'login.html')


def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        if not username or not email or not password or not confirm_password:
            return render(request, 'signup.html', {'error': 'All fields are required'})

        if password != confirm_password:
            return render(request, 'signup.html', {'error': 'Passwords do not match'})

        if User.objects.filter(username=username).exists():
            return render(request, 'signup.html', {'error': 'Username already exists'})

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            # Authenticate the user manually
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)  # Log the user in
                return redirect('dashboard')  # Redirect to the dashboard page

            # Fallback if authentication fails
            return render(request, 'signup.html', {'error': 'Authentication failed. Please try logging in.'})

        except IntegrityError:
            return render(request, 'signup.html', {'error': 'Username already exists'})
        except ValueError as e:
            return render(request, 'signup.html', {'error': str(e)})

    return render(request, 'signup.html')


def dashboard_view(request):
    token = request.session.get('token')
    if not token:
        return redirect('login')
    
    # Make an authenticated request using the token if needed
    # Example: headers = {'Authorization': f'Token {token}'}

    return render(request, 'dashboard.html')