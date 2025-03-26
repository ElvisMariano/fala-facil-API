"""Admin configuration for flashcards app."""

from django.contrib import admin
from django.utils.translation import gettext_lazy as _

from .models import Deck, Flashcard, FlashcardProgress


@admin.register(Deck)
class DeckAdmin(admin.ModelAdmin):
    """Admin interface for Deck model."""

    list_display = [
        'name',
        'language',
        'level',
        'category',
        'is_public',
        'owner',
        'flashcards_count',
        'created_at',
    ]
    list_filter = [
        'language',
        'level',
        'category',
        'is_public',
        'created_at',
    ]
    search_fields = [
        'name',
        'description',
        'owner__username',
    ]
    ordering = ['-created_at']
    readonly_fields = [
        'created_at',
        'updated_at',
    ]
    fieldsets = [
        (None, {
            'fields': [
                'name',
                'description',
                'language',
                'level',
                'category',
                'is_public',
                'owner',
            ],
        }),
        (_('Datas'), {
            'fields': [
                'created_at',
                'updated_at',
            ],
        }),
    ]

    def flashcards_count(self, obj):
        """Return number of flashcards in deck."""
        return obj.flashcards.count()
    flashcards_count.short_description = _('Flashcards')


@admin.register(Flashcard)
class FlashcardAdmin(admin.ModelAdmin):
    """Admin interface for Flashcard model."""

    list_display = [
        'front',
        'back',
        'deck',
        'created_at',
    ]
    list_filter = [
        'deck__language',
        'deck__level',
        'deck__category',
        'created_at',
    ]
    search_fields = [
        'front',
        'back',
        'example',
        'deck__name',
    ]
    ordering = ['deck', 'created_at']
    readonly_fields = [
        'created_at',
        'updated_at',
    ]
    fieldsets = [
        (None, {
            'fields': [
                'deck',
                'front',
                'back',
                'example',
            ],
        }),
        (_('Mídia'), {
            'fields': [
                'audio',
                'image',
            ],
        }),
        (_('Datas'), {
            'fields': [
                'created_at',
                'updated_at',
            ],
        }),
    ]


@admin.register(FlashcardProgress)
class FlashcardProgressAdmin(admin.ModelAdmin):
    list_display = ('user', 'flashcard', 'correct_attempts', 'incorrect_attempts', 'streak', 'next_review_date')
    list_filter = ('user', 'next_review_date')
    search_fields = ('user__username', 'flashcard__front')
    ordering = ('next_review_date',) 