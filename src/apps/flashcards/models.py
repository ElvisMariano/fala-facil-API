"""Models for flashcards app."""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _

LEVEL_CHOICES = [
    ('A1', _('Iniciante')),
    ('A2', _('Básico')),
    ('B1', _('Intermediário')),
    ('B2', _('Intermediário Superior')),
    ('C1', _('Avançado')),
    ('C2', _('Proficiente')),
]

class Deck(models.Model):
    """Model for flashcard decks."""

    name = models.CharField(
        _('nome'),
        max_length=100,
    )
    description = models.TextField(
        _('descrição'),
        blank=True,
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
    )
    level = models.CharField(
        _('nível'),
        max_length=2,
        choices=LEVEL_CHOICES,
    )
    category = models.CharField(
        _('categoria'),
        max_length=50,
        choices=[
            ('vocabulary', _('Vocabulário')),
            ('grammar', _('Gramática')),
            ('phrases', _('Frases')),
            ('conversation', _('Conversação')),
            ('business', _('Negócios')),
            ('travel', _('Viagem')),
        ],
    )
    is_public = models.BooleanField(
        _('é público'),
        default=True,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('proprietário'),
        on_delete=models.CASCADE,
        related_name='decks',
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

        verbose_name = _('deck')
        verbose_name_plural = _('decks')
        ordering = ['-created_at']

    def __str__(self):
        """Return string representation."""
        return self.name


class Flashcard(models.Model):
    """Model for flashcards."""

    deck = models.ForeignKey(
        Deck,
        verbose_name=_('deck'),
        on_delete=models.CASCADE,
        related_name='flashcards',
    )
    front = models.TextField(
        _('frente'),
    )
    back = models.TextField(
        _('verso'),
    )
    example = models.TextField(
        _('exemplo'),
        blank=True,
    )
    audio = models.FileField(
        _('áudio'),
        upload_to='flashcards/audio/',
        blank=True,
        null=True,
    )
    image = models.ImageField(
        _('imagem'),
        upload_to='flashcards/images/',
        blank=True,
        null=True,
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

        verbose_name = _('flashcard')
        verbose_name_plural = _('flashcards')
        ordering = ['deck', 'created_at']

    def __str__(self):
        """Return string representation."""
        return f'{self.deck.name} - {self.front}'

    def get_audio_url(self):
        """Return audio URL."""
        if self.audio:
            return self.audio.url
        return None

    def get_image_url(self):
        """Return image URL."""
        if self.image:
            return self.image.url
        return None


class FlashcardProgress(models.Model):
    """
    Modelo para rastrear o progresso do usuário em cada flashcard.
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    flashcard = models.ForeignKey('Flashcard', on_delete=models.CASCADE)
    correct_attempts = models.IntegerField(default=0)
    incorrect_attempts = models.IntegerField(default=0)
    average_response_time = models.FloatField(default=0)
    last_reviewed = models.DateTimeField(null=True)
    next_review_date = models.DateTimeField(null=True)
    ease_factor = models.FloatField(default=2.5)
    interval = models.IntegerField(default=1)
    streak = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['user', 'flashcard']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['flashcard']),
            models.Index(fields=['next_review_date'])
        ]
        ordering = ['next_review_date']

    def __str__(self):
        return f"{self.user.username} - {self.flashcard.front} ({self.streak} streak)"

    def calculate_next_review(self, quality: int) -> None:
        """
        Implementa o algoritmo SuperMemo 2 para calcular a próxima data de revisão.
        
        Args:
            quality (int): Qualidade da resposta (0-5)
                0 - Blackout total
                1 - Resposta incorreta, mas lembrou ao ver
                2 - Resposta incorreta, mas parecia fácil de lembrar
                3 - Resposta correta, mas com esforço significativo
                4 - Resposta correta após leve hesitação
                5 - Resposta correta, perfeita
        """
        # Atualiza o fator de facilidade
        self.ease_factor = max(1.3, self.ease_factor + (0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02)))

        # Atualiza o intervalo
        if quality < 3:
            self.interval = 1
            self.streak = 0
        else:
            if self.interval == 1:
                self.interval = 6
            elif self.interval == 6:
                self.interval = 1
            else:
                self.interval = round(self.interval * self.ease_factor)
            self.streak += 1

        # Atualiza as estatísticas
        if quality >= 3:
            self.correct_attempts += 1
        else:
            self.incorrect_attempts += 1

        from datetime import datetime, timedelta
        self.last_reviewed = datetime.now()
        self.next_review_date = datetime.now() + timedelta(days=self.interval) 