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
from django.shortcuts import render, redirect


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


# Root
@login_required(login_url='login')
@api_view(["GET"])
def root(request):
    return render(request, 'dashboard.html')

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

        errors = {}

        # Validate the form input
        if not username or not password:
            errors['general'] = 'All fields are required.'
        else:
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)  # Log the user in
                return redirect(reverse('upload_sales'))  # Redirect to the desired page after login
            else:
                errors['authentication'] = 'Authentication failed. Please check your username and password.'

        # If there are errors, render the login page with errors
        return render(request, 'login.html', {'errors': errors, 'form_data': request.POST})

    # For GET requests, simply render the login page
    return render(request, 'login.html')


def signup_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm-password')

        errors = {}

        if not username or not email or not password or not confirm_password:
            errors['general'] = 'All fields are required'

        if password != confirm_password:
            errors['password'] = 'Passwords do not match'

        if User.objects.filter(username=username).exists():
            errors['username'] = 'Username already exists'

        if errors:
            return render(request, 'signup.html', {'errors': errors, 'form_data': request.POST})

        try:
            user = User.objects.create_user(username=username, email=email, password=password)
            user.save()

            # Authenticate the user
            user = authenticate(request, username=username, password=password)
            if user is not None:
                auth_login(request, user)
                return redirect('update_profile')  # Redirect to the profile update page

            # Fallback if authentication fails
            errors['authentication'] = 'Authentication failed. Please try logging in.'
            return render(request, 'signup.html', {'errors': errors, 'form_data': request.POST})

        except IntegrityError:
            errors['username'] = 'Username already exists'
            return render(request, 'signup.html', {'errors': errors, 'form_data': request.POST})
        except ValueError as e:
            errors['general'] = str(e)
            return render(request, 'signup.html', {'errors': errors, 'form_data': request.POST})

    return render(request, 'signup.html')


class ProfileUpdateView(LoginRequiredMixin, UpdateView):
    model = Profile
    form_class = ProfileUpdateForm
    template_name = 'update_profile.html'
    success_url = reverse_lazy('dashboard_view')

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if email and User.objects.filter(email=email).exclude(pk=self.instance.user.pk).exists():
            raise forms.ValidationError('This email address is already in use. Please supply a different email address.')
        return email

    def get_object(self, queryset=None):
        """
        Retrieve the Profile instance for the logged-in user.
        If no Profile exists, create one and return it.
        """
        try:
            profile = Profile.objects.get(user=self.request.user)
        except Profile.DoesNotExist:
            # Create a profile if it doesn't exist
            profile = Profile.objects.create(user=self.request.user)
        return profile


class ProfileView(LoginRequiredMixin, DetailView):
    model = Profile
    template_name = 'profile.html'
    context_object_name = 'profile'

    def get_object(self):
        # Fetch the Profile instance associated with the logged-in user
        return get_object_or_404(Profile, user=self.request.user)
