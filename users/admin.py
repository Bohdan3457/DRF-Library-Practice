from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from users.models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ("email", "is_staff", "is_active")
    search_fields = ("email",)
    ordering = ("email",)
