from django.db.models.base import Model as Model
from django.db.models.query import QuerySet
from rest_framework.decorators import api_view
from rest_framework.response import Response

from .serializers import UserSerializer
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



class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    success_url = reverse_lazy('dashboard_view')  # Optional, won't be used in JSON response

    def get_object(self, queryset=None):
        """
        Retrieve the Profile instance for the logged-in user.
        If no Profile exists, create one and return it.
        """
        profile, created = Profile.objects.get_or_create(user=self.request.user)
        return profile

    def form_valid(self, form):
        # Validate the form and save the profile
        self.object = form.save()
        response_data = {
            'message': 'Profile updated successfully.',
            'profile': {
                'username': self.object.user.username,
                'email': self.object.user.email,
                'first_name': self.object.first_name,
                'last_name': self.object.last_name,
                'profile_picture': self.object.profile_picture.url if self.object.profile_picture else None,
                'company_name': self.object.company_name,
                'gender': self.object.gender,
                'mobile_number': self.object.mobile_number,
            }
        }
        return JsonResponse(response_data, status=200)

    def form_invalid(self, form):
        # Return validation errors as JSON
        errors = form.errors.as_json()
        return JsonResponse({'errors': errors}, status=400)

    def clean_email(self):
        # Ensure email is unique
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.instance.user.pk).exists():
            raise forms.ValidationError('This email address is already in use. Please supply a different email address.')
        return email


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
