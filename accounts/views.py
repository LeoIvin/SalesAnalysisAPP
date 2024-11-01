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



class ProfileUpdateView(LoginRequiredMixin, APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self):
        """
        Retrieve the Profile instance for the logged-in user.
        """
        return get_object_or_404(Profile, user=self.request.user)

    def patch(self, request, *args, **kwargs):
        profile = self.get_object
        serializer = ProfileSerializer(profile, data=request.data, partial=True) # Allow partial updates

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile

    def get(self, request, *args, **kwargs):
        # Fetch the Profile instance associated with the logged-in user
        profile = self.get_object()

        # Prepare the profile data as a JSON response
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

        return JsonResponse(profile_data)

    def get_object(self):
        # Fetch the Profile instance associated with the logged-in user
        return get_object_or_404(Profile, user=self.request.user)
