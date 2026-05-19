from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display  = ['email', 'get_full_name', 'role', 'is_superuser', 'is_approved', 'is_active', 'date_joined']
    list_filter   = ['role', 'is_superuser', 'is_approved', 'is_active']
    search_fields = ['email', 'username', 'first_name', 'last_name']
    ordering      = ['-date_joined']

    fieldsets = (
        (None, {'fields': ('email', 'username', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'phone', 'date_of_birth', 'gender', 'address', 'bio', 'profile_image')}),
        ('Security', {'fields': ('security_question', 'security_answer')}),
        ('Roles & Permissions', {'fields': ('role', 'is_approved', 'is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('date_joined', 'last_login')}),
    )
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'username', 'first_name', 'last_name', 'role', 'is_approved', 'password1', 'password2'),
        }),
    )

    def has_delete_permission(self, request, obj=None):
        # Nobody can delete a superuser via admin panel (only another superuser can, and only via shell)
        if obj and obj.is_superuser and not request.user.is_superuser:
            return False
        return super().has_delete_permission(request, obj)

    def get_readonly_fields(self, request, obj=None):
        # Only superuser can change is_superuser field
        if not request.user.is_superuser:
            return ['is_superuser', 'is_staff']
        return []
