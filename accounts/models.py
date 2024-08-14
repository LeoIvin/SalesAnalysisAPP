from django.db import models
from django.contrib.auth.models import AbstractBaseUser, BaseUserManager
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.db.models.signals import post_save
from django.dispatch import receiver

class AppUserManager(BaseUserManager):
      def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError(_('An email is required.'))
        if not password:
            raise ValueError('A password is required.')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save()
        return user
      
      def create_superuser(self, email, password=None, **extra_fields):
          extra_fields.setdefault("is_staff", True)
          extra_fields.setdefault("is_superuser", True)
          if extra_fields.get("is_staff") is not True:
              raise ValueError(_("Superuser must have is_staff=True."))
          if extra_fields.get("is_superuser") is not True:
              raise ValueError(_("Superuser must have is_superuser=True."))
          return self.create_user(email, password, **extra_fields)
      

class AppUser(AbstractBaseUser):
    name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone_number = models.CharField(null=True, max_length=20)
    is_staff = models.BooleanField(_("staff status"), default=False)
    is_active = models.BooleanField(_("active"), default=True)
    date_joined = models.DateTimeField(_("date joined"), auto_now_add=True)
    is_email_verified = models.BooleanField(_("email verified"), default=False)

    def date_created(self):
        # Format the date_joined attribute as "DD-MM-YY"
        return self.date_joined.strftime("%d-%m-%y")
    
    def __str__(self):
        return self.email
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['name']
    objects = AppUserManager()

    def __str__(self):
        return self.username