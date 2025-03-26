"""Configuration for users app."""

from django.apps import AppConfig


class UsersConfig(AppConfig):
    """Configuration class for users app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.users'
    verbose_name = 'Usuários'

    def ready(self):
        """Import signals when app is ready."""
        import apps.users.signals  # noqa 