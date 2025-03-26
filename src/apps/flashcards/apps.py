"""Configuration for flashcards app."""

from django.apps import AppConfig


class FlashcardsConfig(AppConfig):
    """Configuration class for flashcards app."""

    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.flashcards'
    verbose_name = 'Flashcards'

    def ready(self):
        """Import signals when app is ready."""
        import apps.flashcards.signals  # noqa 