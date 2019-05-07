from django.contrib import admin

# Register your models here.
from users.models import Profile, UserConfirmation


class UserAdmin(admin.ModelAdmin):


    model = Profile
    list_display = ['email','username','first_name','last_name','is_verified',]


class UserConfirmationadmin(admin.ModelAdmin):
    model = UserConfirmation

    list_display = ['user',]

admin.site.register(Profile,UserAdmin)
admin.site.register(UserConfirmation,UserConfirmationadmin)
