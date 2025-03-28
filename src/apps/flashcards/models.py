"""Models for flashcards app."""

from django.conf import settings
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

LEVEL_CHOICES = [
    ('A1', _('Iniciante')),
    ('A2', _('Básico')),
    ('B1', _('Intermediário')),
    ('B2', _('Intermediário Superior')),
    ('C1', _('Avançado')),
    ('C2', _('Proficiente')),
]

CATEGORY_CHOICES = [
    ('vocabulary', _('Vocabulário')),
    ('grammar', _('Gramática')),
    ('pronunciation', _('Pronúncia')),
    ('expressions', _('Expressões')),
    ('conversation', _('Conversação')),
    ('reading', _('Leitura')),
    ('writing', _('Escrita')),
    ('listening', _('Compreensão Auditiva')),
]

LANGUAGE_CHOICES = [
    ('en', _('Inglês')),
    ('es', _('Espanhol')),
    ('fr', _('Francês')),
    ('de', _('Alemão')),
    ('it', _('Italiano')),
    ('pt', _('Português')),
    ('ja', _('Japonês')),
    ('ko', _('Coreano')),
    ('zh', _('Chinês')),
    ('ru', _('Russo')),
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
        choices=LANGUAGE_CHOICES,
    )
    level = models.CharField(
        _('nível'),
        max_length=2,
        choices=LEVEL_CHOICES,
    )
    category = models.CharField(
        _('categoria'),
        max_length=20,
        choices=CATEGORY_CHOICES,
    )
    owner = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('proprietário'),
        on_delete=models.CASCADE,
        related_name='decks',
    )
    is_public = models.BooleanField(
        _('público'),
        default=True,
        help_text=_('Se marcado, o deck ficará visível para todos os usuários.'),
    )
    is_featured = models.BooleanField(
        _('destaque'),
        default=False,
        help_text=_('Se marcado, o deck aparecerá na seção de destaques.'),
    )
    is_archived = models.BooleanField(
        _('arquivado'),
        default=False,
        help_text=_('Se marcado, o deck será arquivado e não aparecerá nas listagens.'),
    )
    tags = models.CharField(
        _('tags'),
        max_length=200,
        blank=True,
        help_text=_('Tags separadas por vírgula.'),
    )
    difficulty = models.FloatField(
        _('dificuldade'),
        default=0.0,
        help_text=_('Dificuldade média do deck (0.0 a 1.0).'),
    )
    total_cards = models.PositiveIntegerField(
        _('total de cartões'),
        default=0,
        help_text=_('Total de cartões no deck.'),
    )
    mastered_cards = models.PositiveIntegerField(
        _('cartões dominados'),
        default=0,
        help_text=_('Total de cartões dominados pelos usuários.'),
    )
    average_mastery_time = models.FloatField(
        _('tempo médio de domínio'),
        default=0.0,
        help_text=_('Tempo médio para dominar os cartões (em dias).'),
    )
    study_count = models.PositiveIntegerField(
        _('contagem de estudos'),
        default=0,
        help_text=_('Número de vezes que o deck foi estudado.'),
    )
    favorite_count = models.PositiveIntegerField(
        _('contagem de favoritos'),
        default=0,
        help_text=_('Número de usuários que favoritaram o deck.'),
    )
    share_count = models.PositiveIntegerField(
        _('contagem de compartilhamentos'),
        default=0,
        help_text=_('Número de vezes que o deck foi compartilhado.'),
    )
    # Novos campos
    color = models.CharField(
        _('cor'),
        max_length=7,
        default='#FFFFFF',
        help_text=_('Cor do deck em formato hexadecimal.'),
    )
    icon = models.CharField(
        _('ícone'),
        max_length=50,
        default='book',  # Ícone padrão
        help_text=_('Nome do ícone do deck.'),
    )
    due_cards = models.PositiveIntegerField(
        _('cartões pendentes'),
        default=0,
        help_text=_('Número de cartões pendentes para revisão.'),
    )
    last_studied_at = models.DateTimeField(
        _('último estudo'),
        null=True,
        blank=True,
        default=None,
        help_text=_('Data e hora do último estudo do deck.'),
    )
    completion_rate = models.FloatField(
        _('taxa de conclusão'),
        default=0.0,
        help_text=_('Taxa de conclusão do deck (0.0 a 1.0).'),
    )
    version = models.CharField(
        _('versão'),
        max_length=10,
        default='1.0.0',
        help_text=_('Versão do deck no formato semântico.'),
    )
    parent_deck = models.ForeignKey(
        'self',
        verbose_name=_('deck original'),
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        default=None,
        related_name='derived_decks',
        help_text=_('Deck original em caso de cópia.'),
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
        ordering = ['name']
        indexes = [
            models.Index(fields=['language']),
            models.Index(fields=['level']),
            models.Index(fields=['category']),
            models.Index(fields=['owner']),
            models.Index(fields=['created_at']),
            models.Index(fields=['is_public']),
            models.Index(fields=['is_featured']),
            models.Index(fields=['is_archived']),
            models.Index(fields=['difficulty']),
            models.Index(fields=['study_count']),
            models.Index(fields=['favorite_count']),
            models.Index(fields=['due_cards']),
            models.Index(fields=['last_studied_at']),
            models.Index(fields=['completion_rate']),
            models.Index(fields=['version']),
        ]

    def __str__(self):
        """Return string representation."""
        return self.name

    def update_stats(self):
        """Update deck statistics."""
        # Atualiza total de cartões
        self.total_cards = self.flashcards.count()

        # Atualiza cartões dominados e pendentes
        from apps.progress.models import FlashcardProgress
        mastered = FlashcardProgress.objects.filter(
            flashcard__deck=self,
            mastered=True,
        ).count()
        self.mastered_cards = mastered

        # Atualiza cartões pendentes
        self.due_cards = FlashcardProgress.objects.filter(
            flashcard__deck=self,
            next_review_date__lte=timezone.now(),
        ).count()

        # Atualiza taxa de conclusão
        if self.total_cards > 0:
            self.completion_rate = self.mastered_cards / self.total_cards
            self.difficulty = 1 - self.completion_rate

        # Atualiza tempo médio de domínio
        from django.db.models import Avg
        avg_time = FlashcardProgress.objects.filter(
            flashcard__deck=self,
            mastered=True,
        ).aggregate(
            avg_time=Avg('days_to_master'),
        )['avg_time'] or 0.0
        self.average_mastery_time = avg_time

        self.save()

    def duplicate(self, new_owner=None):
        """Create a copy of the deck."""
        # Remove campos únicos e específicos
        deck_data = {
            'name': f'Cópia de {self.name}',
            'description': self.description,
            'language': self.language,
            'level': self.level,
            'category': self.category,
            'owner': new_owner or self.owner,
            'is_public': False,
            'tags': self.tags,
            'color': self.color,
            'icon': self.icon,
            'version': '1.0.0',
            'parent_deck': self,
        }

        # Cria novo deck
        new_deck = Deck.objects.create(**deck_data)

        # Copia os flashcards
        for flashcard in self.flashcards.all():
            flashcard.pk = None
            flashcard.deck = new_deck
            flashcard.save()

        return new_deck

    def archive(self):
        """Archive the deck."""
        self.is_archived = True
        self.is_public = False
        self.is_featured = False
        self.save()

    def unarchive(self):
        """Unarchive the deck."""
        self.is_archived = False
        self.save()

    def feature(self):
        """Feature the deck."""
        if self.is_public and not self.is_archived:
            self.is_featured = True
            self.save()

    def unfeature(self):
        """Unfeature the deck."""
        self.is_featured = False
        self.save()

    def increment_study_count(self):
        """Increment study count and update last studied date."""
        self.study_count += 1
        self.last_studied_at = timezone.now()
        self.save()

    def increment_favorite_count(self):
        """Increment favorite count."""
        self.favorite_count += 1
        self.save()

    def decrement_favorite_count(self):
        """Decrement favorite count."""
        if self.favorite_count > 0:
            self.favorite_count -= 1
            self.save()

    def increment_share_count(self):
        """Increment share count."""
        self.share_count += 1
        self.save()

    def update_version(self, version_type='patch'):
        """Update deck version."""
        major, minor, patch = map(int, self.version.split('.'))
        if version_type == 'major':
            major += 1
            minor = 0
            patch = 0
        elif version_type == 'minor':
            minor += 1
            patch = 0
        else:  # patch
            patch += 1
        self.version = f'{major}.{minor}.{patch}'
        self.save()


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


class DeckFavorite(models.Model):
    """Model for deck favorites."""

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        verbose_name=_('usuário'),
        on_delete=models.CASCADE,
        related_name='favorite_decks',
    )
    deck = models.ForeignKey(
        'Deck',
        verbose_name=_('deck'),
        on_delete=models.CASCADE,
        related_name='favorites',
    )
    created_at = models.DateTimeField(
        _('criado em'),
        auto_now_add=True,
    )

    class Meta:
        """Meta options."""

        verbose_name = _('deck favorito')
        verbose_name_plural = _('decks favoritos')
        unique_together = ['user', 'deck']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user']),
            models.Index(fields=['deck']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        """Return string representation."""
        return f'{self.user.username} - {self.deck.name}'

    def save(self, *args, **kwargs):
        """Override save method."""
        is_new = self.pk is None
        super().save(*args, **kwargs)
        if is_new:
            self.deck.increment_favorite_count()

    def delete(self, *args, **kwargs):
        """Override delete method."""
        self.deck.decrement_favorite_count()
        super().delete(*args, **kwargs) 