"""Signals for flashcards app."""

from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver

from .models import Flashcard


@receiver(pre_save, sender=Flashcard)
def delete_old_files(sender, instance, **kwargs):
    """Delete old files when updating a flashcard."""
    if not instance.pk:
        return

    try:
        old_instance = sender.objects.get(pk=instance.pk)
        if old_instance.audio and old_instance.audio != instance.audio:
            old_instance.audio.delete(save=False)
        if old_instance.image and old_instance.image != instance.image:
            old_instance.image.delete(save=False)
    except sender.DoesNotExist:
        return


@receiver(post_delete, sender=Flashcard)
def delete_files(sender, instance, **kwargs):
    """Delete files when deleting a flashcard."""
    if instance.audio:
        instance.audio.delete(save=False)
    if instance.image:
        instance.image.delete(save=False) 