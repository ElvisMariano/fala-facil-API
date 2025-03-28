"""Models for users app."""

from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils.translation import gettext_lazy as _


class User(AbstractUser):
    """Custom user model."""

    # Campos padrão do AbstractUser:
    # username, first_name, last_name, email, is_staff, is_active, date_joined

    # Campos personalizados
    email = models.EmailField(
        _('endereço de e-mail'),
        unique=True,
        error_messages={
            'unique': _('Um usuário com este e-mail já existe.'),
        },
    )
    avatar = models.ImageField(
        _('avatar'),
        upload_to='avatars/',
        blank=True,
        null=True,
    )
    bio = models.TextField(
        _('biografia'),
        blank=True,
        default='',
    )
    language = models.CharField(
        _('idioma'),
        max_length=2,
        choices=[
            ('en', _('Inglês')),
            ('es', _('Espanhol')),
            ('fr', _('Francês')),
            ('de', _('Alemão')),
            ('it', _('Italiano')),
            ('pt', _('Português')),
        ],
        default='en',
    )
    level = models.PositiveIntegerField(
        _('nível'),
        default=1,
    )
    experience = models.PositiveIntegerField(
        _('experiência'),
        default=0,
    )
    streak = models.PositiveIntegerField(
        _('sequência'),
        default=0,
    )
    last_activity = models.DateTimeField(
        _('última atividade'),
        auto_now=True,
    )
    is_premium = models.BooleanField(
        _('é premium'),
        default=False,
    )

    class Meta:
        """Meta options."""
        verbose_name = _('usuário')
        verbose_name_plural = _('usuários')
        ordering = ['-date_joined']

    def __str__(self):
        """Return string representation."""
        return self.get_full_name() or self.username

    def get_avatar_url(self):
        """Return avatar URL."""
        if self.avatar:
            return self.avatar.url
        return None

    def add_experience(self, amount):
        """Add experience points to user."""
        self.experience += amount
        self.save() 