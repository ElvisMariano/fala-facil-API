"""Admin configuration for users app."""

from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _

User = get_user_model()


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    """Admin interface for user model."""

    list_display = [
        'username',
        'email',
        'first_name',
        'last_name',
        'language',
        'level',
        'experience',
        'streak',
        'is_premium',
        'is_staff',
        'is_active',
    ]
    list_filter = [
        'is_staff',
        'is_active',
        'is_premium',
        'language',
        'level',
        'date_joined',
        'last_activity',
    ]
    search_fields = [
        'username',
        'email',
        'first_name',
        'last_name',
    ]
    ordering = ['-date_joined']
    readonly_fields = [
        'date_joined',
        'last_login',
        'last_activity',
    ]
    fieldsets = [
        (None, {
            'fields': [
                'username',
                'password',
            ],
        }),
        (_('Informações pessoais'), {
            'fields': [
                'first_name',
                'last_name',
                'email',
                'avatar',
                'bio',
            ],
        }),
        (_('Progresso'), {
            'fields': [
                'language',
                'level',
                'experience',
                'streak',
                'is_premium',
            ],
        }),
        (_('Permissões'), {
            'fields': [
                'is_active',
                'is_staff',
                'is_superuser',
                'groups',
                'user_permissions',
            ],
        }),
        (_('Datas importantes'), {
            'fields': [
                'last_login',
                'date_joined',
                'last_activity',
            ],
        }),
    ]
    add_fieldsets = [
        (None, {
            'classes': ['wide'],
            'fields': [
                'username',
                'email',
                'password1',
                'password2',
            ],
        }),
    ] 