"""Services for flashcards app."""

import json
import csv
import io
from typing import List, Dict, Any, Union
from django.db.models import Q, Count, Avg, F
from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.conf import settings
from django.core.files.base import ContentFile
from django.utils.text import slugify

from .models import Deck, DeckFavorite, FlashcardProgress, Flashcard

User = get_user_model()


class DeckRecommendationService:
    """Service for deck recommendations."""

    def __init__(self, user):
        """Initialize service."""
        self.user = user

    def get_recommendations(self, limit=10):
        """Get deck recommendations for user."""
        # Tenta obter recomendações do cache
        cache_key = f'deck_recommendations_{self.user.id}'
        recommendations = cache.get(cache_key)
        if recommendations is not None:
            return recommendations

        # Obtém os decks que o usuário já favoritou
        favorited_decks = DeckFavorite.objects.filter(
            user=self.user,
        ).values_list('deck_id', flat=True)

        # Obtém os decks que o usuário já estudou
        studied_decks = FlashcardProgress.objects.filter(
            user=self.user,
        ).values_list('flashcard__deck_id', flat=True).distinct()

        # Base query para decks públicos não arquivados
        base_query = Deck.objects.filter(
            is_public=True,
            is_archived=False,
        ).exclude(
            id__in=favorited_decks,
        ).exclude(
            id__in=studied_decks,
        ).exclude(
            owner=self.user,
        )

        # Recomendações baseadas no nível do usuário
        user_level_decks = self._get_user_level_recommendations(base_query)

        # Recomendações baseadas nas categorias favoritas
        category_decks = self._get_category_recommendations(base_query)

        # Recomendações baseadas na popularidade
        popular_decks = self._get_popularity_recommendations(base_query)

        # Combina as recomendações
        recommendations = list(user_level_decks[:5])
        recommendations.extend(category_decks[:3])
        recommendations.extend(popular_decks[:2])

        # Remove duplicatas mantendo a ordem
        seen = set()
        unique_recommendations = []
        for deck in recommendations:
            if deck.id not in seen:
                seen.add(deck.id)
                unique_recommendations.append(deck)

        # Limita o número de recomendações
        recommendations = unique_recommendations[:limit]

        # Armazena em cache por 1 hora
        cache.set(cache_key, recommendations, 60 * 60)

        return recommendations

    def _get_user_level_recommendations(self, base_query):
        """Get recommendations based on user level."""
        # Obtém o nível mais comum dos decks que o usuário já estudou
        user_level = FlashcardProgress.objects.filter(
            user=self.user,
        ).values(
            'flashcard__deck__level',
        ).annotate(
            count=Count('flashcard__deck__level'),
        ).order_by('-count').first()

        if user_level:
            return base_query.filter(
                level=user_level['flashcard__deck__level'],
            ).order_by('-favorite_count')
        return base_query.order_by('-favorite_count')

    def _get_category_recommendations(self, base_query):
        """Get recommendations based on user favorite categories."""
        # Obtém as categorias mais comuns dos decks que o usuário já estudou
        favorite_categories = FlashcardProgress.objects.filter(
            user=self.user,
        ).values(
            'flashcard__deck__category',
        ).annotate(
            count=Count('flashcard__deck__category'),
        ).order_by('-count')[:3]

        if favorite_categories:
            categories = [cat['flashcard__deck__category'] for cat in favorite_categories]
            return base_query.filter(
                category__in=categories,
            ).order_by('-favorite_count')
        return base_query.order_by('-favorite_count')

    def _get_popularity_recommendations(self, base_query):
        """Get recommendations based on popularity."""
        return base_query.annotate(
            popularity_score=F('favorite_count') + F('study_count'),
        ).order_by('-popularity_score')


class DeckExportService:
    """Service for deck export."""

    SUPPORTED_FORMATS = ['json', 'csv']

    def __init__(self, deck: Deck):
        """Initialize service."""
        self.deck = deck

    def export(self, format: str = 'json') -> Union[str, bytes]:
        """Export deck to specified format."""
        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(f'Formato não suportado. Use um dos seguintes: {self.SUPPORTED_FORMATS}')

        if format == 'json':
            return self._export_to_json()
        return self._export_to_csv()

    def _export_to_json(self) -> str:
        """Export deck to JSON format."""
        data = self._get_deck_data()
        return json.dumps(data, ensure_ascii=False, indent=2)

    def _export_to_csv(self) -> bytes:
        """Export deck to CSV format."""
        output = io.StringIO()
        writer = csv.writer(output)

        # Escreve o cabeçalho
        writer.writerow(['front', 'back', 'example', 'audio_url', 'image_url'])

        # Escreve os flashcards
        for flashcard in self.deck.flashcards.all():
            writer.writerow([
                flashcard.front,
                flashcard.back,
                flashcard.example,
                flashcard.get_audio_url() or '',
                flashcard.get_image_url() or '',
            ])

        return output.getvalue().encode('utf-8')

    def _get_deck_data(self) -> Dict[str, Any]:
        """Get deck data for export."""
        return {
            'name': self.deck.name,
            'description': self.deck.description,
            'language': self.deck.language,
            'level': self.deck.level,
            'category': self.deck.category,
            'tags': self.deck.tags,
            'flashcards': [
                {
                    'front': card.front,
                    'back': card.back,
                    'example': card.example,
                    'audio_url': card.get_audio_url(),
                    'image_url': card.get_image_url(),
                }
                for card in self.deck.flashcards.all()
            ],
        }


class DeckImportService:
    """Service for deck import."""

    SUPPORTED_FORMATS = ['json', 'csv']

    def __init__(self, user: User):
        """Initialize service."""
        self.user = user

    def import_deck(self, file_content: Union[str, bytes], format: str) -> Deck:
        """Import deck from file content."""
        if format not in self.SUPPORTED_FORMATS:
            raise ValueError(f'Formato não suportado. Use um dos seguintes: {self.SUPPORTED_FORMATS}')

        if format == 'json':
            return self._import_from_json(file_content)
        return self._import_from_csv(file_content)

    def _import_from_json(self, content: str) -> Deck:
        """Import deck from JSON format."""
        try:
            data = json.loads(content)
            return self._create_deck_from_data(data)
        except json.JSONDecodeError:
            raise ValueError('Conteúdo JSON inválido')
        except KeyError as e:
            raise ValueError(f'Campo obrigatório ausente: {e}')

    def _import_from_csv(self, content: bytes) -> Deck:
        """Import deck from CSV format."""
        try:
            # Cria um deck com nome padrão
            deck = Deck.objects.create(
                name='Deck Importado',
                owner=self.user,
                language='en',  # Valor padrão
                level='A1',     # Valor padrão
                category='vocabulary',  # Valor padrão
            )

            # Lê o CSV
            csv_content = content.decode('utf-8')
            reader = csv.DictReader(io.StringIO(csv_content))

            # Cria os flashcards
            for row in reader:
                Flashcard.objects.create(
                    deck=deck,
                    front=row['front'],
                    back=row['back'],
                    example=row.get('example', ''),
                )

            return deck
        except (csv.Error, UnicodeDecodeError):
            if deck.id:
                deck.delete()
            raise ValueError('Arquivo CSV inválido')

    def _create_deck_from_data(self, data: Dict[str, Any]) -> Deck:
        """Create deck from imported data."""
        # Cria o deck
        deck = Deck.objects.create(
            name=data['name'],
            description=data.get('description', ''),
            language=data['language'],
            level=data['level'],
            category=data['category'],
            tags=data.get('tags', ''),
            owner=self.user,
        )

        # Cria os flashcards
        for card_data in data['flashcards']:
            Flashcard.objects.create(
                deck=deck,
                front=card_data['front'],
                back=card_data['back'],
                example=card_data.get('example', ''),
            )

        return deck 