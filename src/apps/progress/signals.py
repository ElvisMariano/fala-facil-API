"""Signals for progress app."""

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

from .models import UserProgress

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_progress(sender, instance, created, **kwargs):
    """Create UserProgress instance when a new user is created."""
    if created:
        UserProgress.objects.create(user=instance)


@receiver(post_save, sender=User)
def save_user_progress(sender, instance, **kwargs):
    """Save UserProgress instance when user is updated."""
    if hasattr(instance, 'progress'):
        instance.progress.save() 