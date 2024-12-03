from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django import forms
from django.utils.safestring import mark_safe
from apps.authkit.models import *


class CustomUserAdmin(UserAdmin):
    model = User
    list_display = ('id', 'username', 'email', 'is_superuser', 'is_active', 'is_verified', 'created_at', 'updated_at')
    list_filter = ('is_active', 'is_staff', 'created_at', 'updated_at')
    search_fields = ('username', 'email')
    ordering = ('-created_at',)

    # Mark created_at and updated_at as readonly fields
    readonly_fields = ('created_at', 'updated_at')

    # Updated fieldsets without non-editable fields
    fieldsets = (
        ('Security', {'fields': ('username', 'email', 'password', 'role', 'batch')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important dates', {'fields': ('last_login', 'created_at', 'updated_at')}),
    )

    # Add username in the add form
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_active', 'is_staff', 'groups', 'user_permissions'),
        }),
    )

    def get_form(self, request, obj=None, **kwargs):
        try:
            form = super().get_form(request, obj, **kwargs)
            form.base_fields['password'].help_text = mark_safe(
                'Raw passwords are not stored, so there is no way to see this user’s password, but you can change the password using <a style="color:#9333EA;" href="../../{}/password/">this form</a>.'.format(obj.pk if obj else '__object_id__')
            )
            return form
        except:
            return super().get_form(request, obj, **kwargs)


# Register the updated CustomUserAdmin
admin.site.register(User, CustomUserAdmin)

admin.site.register(Batch)