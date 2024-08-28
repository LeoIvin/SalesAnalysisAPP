from django.contrib import admin
from .models import Profile

class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'first_name', 'last_name', 'profile_picture', 'company_name', 'gender', 'mobile_number')
    fields = ('user', 'first_name', 'last_name', 'profile_picture', 'company_name', 'gender', 'mobile_number')

admin.site.register(Profile, ProfileAdmin)



