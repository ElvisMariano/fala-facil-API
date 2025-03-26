"""Models for progress app."""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

from apps.flashcards.models import LEVEL_CHOICES


class UserProgress(models.Model):
    """Model for tracking user progress."""

    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        verbose_name=_('usuário'),
        on_delete=models.CASCADE,
        related_name='progress',
    )
    current_level = models.CharField(
        _('nível atual'),
        max_length=2,
        choices=LEVEL_CHOICES,
        default='A1',
    )
    total_cards = models.IntegerField(
        _('total de cartões'),
        default=0,
    )
    mastered_cards = models.IntegerField(
        _('cartões dominados'),
        default=0,
    )
    current_streak = models.IntegerField(
        _('sequência atual'),
        default=0,
    )
    longest_streak = models.IntegerField(
        _('maior sequência'),
        default=0,
    )
    accuracy_rate = models.FloatField(
        _('taxa de acerto'),
        default=0,
    )
    average_response_time = models.FloatField(
        _('tempo médio de resposta'),
        default=0,
    )
    cards_per_day = models.IntegerField(
        _('cartões por dia'),
        default=0,
    )
    time_spent = models.IntegerField(
        _('tempo gasto'),
        help_text=_('Tempo total gasto estudando em minutos'),
        default=0,
    )
    last_study_date = models.DateTimeField(
        _('última data de estudo'),
        null=True,
        blank=True,
    )
    created_at = models.DateTimeField(
        _('criado em'),
        auto_now_add=True,
    )
    updated_at = models.DateTimeField(
        _('atualizado em'),
        auto_now=True,
    )

    class Meta:
        """Meta options."""

        verbose_name = _('progresso do usuário')
        verbose_name_plural = _('progressos dos usuários')
        ordering = ['-updated_at']

    def __str__(self):
        """Return string representation."""
        return f'{self.user.username} - {self.current_level}'

    def update_streak(self):
        """Update user streak."""
        from django.utils import timezone
        from datetime import timedelta

        now = timezone.now()
        if self.last_study_date:
            # Se o último estudo foi há mais de 48 horas, reseta a sequência
            if now - self.last_study_date > timedelta(hours=48):
                self.current_streak = 0
            # Se o último estudo foi no dia anterior, incrementa a sequência
            elif now.date() - self.last_study_date.date() == timedelta(days=1):
                self.current_streak += 1
                if self.current_streak > self.longest_streak:
                    self.longest_streak = self.current_streak
        self.last_study_date = now
        self.save()

    def update_stats(self, correct_attempts=0, incorrect_attempts=0, response_time=0):
        """Update user statistics."""
        total_attempts = correct_attempts + incorrect_attempts
        if total_attempts > 0:
            self.accuracy_rate = (correct_attempts / total_attempts) * 100
            self.average_response_time = response_time
            self.total_cards = total_attempts
            self.mastered_cards = correct_attempts
            self.save() 