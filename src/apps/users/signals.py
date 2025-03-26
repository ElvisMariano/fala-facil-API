"""Signals for users app."""

from django.contrib.auth import get_user_model
from django.db.models.signals import post_save
from django.dispatch import receiver

User = get_user_model()


@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """Create user profile when user is created."""
    if created:
        # Aqui você pode adicionar lógica para criar perfis relacionados
        # ou executar outras ações quando um usuário é criado
        pass 