"""Configuration for progress app."""

from django.apps import AppConfig


class ProgressConfig(AppConfig):
    """Configuration class for progress app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.progress'
    verbose_name = 'Progresso'

    def ready(self):
        """Import signals when app is ready."""
        import apps.progress.signals  # noqa 