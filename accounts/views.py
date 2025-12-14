from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import UserSerializer, ProfileSerializer
from rest_framework import status
from rest_framework.authtoken.models import Token
from django.contrib.auth.models import User
from django.db import IntegrityError

from django.shortcuts import get_object_or_404


from rest_framework.decorators import authentication_classes, permission_classes
from rest_framework.authentication import SessionAuthentication, TokenAuthentication
from rest_framework.permissions import IsAuthenticated

import requests
from django.urls import reverse

from django.contrib.auth import authenticate, login as auth_login

from django.http import JsonResponse
from django.contrib.auth.decorators import login_required

from django.views.generic.edit import UpdateView
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from .models import Profile
from .forms import ProfileUpdateForm
from django.forms import forms

from rest_framework.views import APIView
from django.views.decorators.csrf import csrf_exempt


# DRF API Views
@api_view(["POST"])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")
    email = request.data.get("email")

    if (not username and not email) or not password:
        return Response({"error": "Username/Email and password are required."}, status=status.HTTP_400_BAD_REQUEST)
    
    if not username and email:
        try:
            user = User.objects.get(email=email)
            username = user.username
        except User.DoesNotExist:
            return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
    
    user = authenticate(username=username, password=password)

    if user is None:
        print(f"Invalid credentials for user: {username}")
        return Response({"error": "Invalid credentials."}, status=status.HTTP_401_UNAUTHORIZED)
    
    # Generate or retrieve token
    token, created = Token.objects.get_or_create(user=user)

    serializer = UserSerializer(user)

    return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_200_OK)


@api_view(["POST"])
def signup(request):
    serializer = UserSerializer(data=request.data)

    if serializer.is_valid():
        user = serializer.save()
        user.set_password(request.data['password']) # Hash the password
        user.save()

        # Generate a token for the new user
        token = Token.objects.create(user=user)
        
        # Return token and user data
        return Response({"token": token.key, "user": serializer.data}, status=status.HTTP_201_CREATED)
    
    # Handle invalid data by returning validation errors
    print(f"Signup validation errors: {serializer.errors}")
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        

@api_view(['GET'])
@authentication_classes([SessionAuthentication, TokenAuthentication])
@permission_classes([IsAuthenticated])
def test_token(request):
    return Response(f"passed for {request.user.username}")



# Profile Update View using APIView
class ProfileUpdateView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_object(self):
        # Retrieve the Profile instance for the logged-in user
        return get_object_or_404(Profile, user=self.request.user)

    def patch(self, request, *args, **kwargs):
        profile = self.get_object()
        serializer = ProfileSerializer(profile, data=request.data, partial=True)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Profile Detail View using APIView
class ProfileView(APIView):
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        # Fetch the Profile instance associated with the logged-in user
        profile = get_object_or_404(Profile, user=request.user)
        profile_data = {
            'username': profile.user.username,
            'email': profile.user.email,
            'first_name': profile.first_name,
            'last_name': profile.last_name,
            'profile_picture': profile.profile_picture.url if profile.profile_picture else None,
            'company_name': profile.company_name,
            'gender': profile.gender,
            'mobile_number': profile.mobile_number,
        }
        return JsonResponse(profile_data, status=200)


