"""Tests for flashcards services."""

import json
from django.test import TestCase
from django.contrib.auth import get_user_model
from django.core.cache import cache

from ..models import Deck, DeckFavorite, Flashcard, FlashcardProgress
from ..services import DeckRecommendationService, DeckExportService, DeckImportService

User = get_user_model()


class DeckRecommendationServiceTests(TestCase):
    """Test the deck recommendation service."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )

        # Cria decks com diferentes níveis e categorias
        self.deck1 = Deck.objects.create(
            name='Deck 1',
            language='en',
            level='A1',
            category='vocabulary',
            owner=self.user,
            is_public=True,
        )
        self.deck2 = Deck.objects.create(
            name='Deck 2',
            language='en',
            level='A2',
            category='grammar',
            owner=self.user,
            is_public=True,
        )
        self.deck3 = Deck.objects.create(
            name='Deck 3',
            language='en',
            level='A1',
            category='vocabulary',
            owner=self.user,
            is_public=True,
        )

        # Cria flashcards e progresso
        self.flashcard1 = Flashcard.objects.create(
            deck=self.deck1,
            front='Front 1',
            back='Back 1',
        )
        self.flashcard2 = Flashcard.objects.create(
            deck=self.deck2,
            front='Front 2',
            back='Back 2',
        )
        self.progress1 = FlashcardProgress.objects.create(
            user=self.user,
            flashcard=self.flashcard1,
            correct_attempts=5,
        )
        self.progress2 = FlashcardProgress.objects.create(
            user=self.user,
            flashcard=self.flashcard2,
            correct_attempts=3,
        )

    def tearDown(self):
        """Clean up after tests."""
        cache.clear()

    def test_get_recommendations(self):
        """Test getting deck recommendations."""
        service = DeckRecommendationService(self.user)
        recommendations = service.get_recommendations()

        self.assertEqual(len(recommendations), 1)
        self.assertEqual(recommendations[0], self.deck3)

    def test_recommendations_exclude_favorited(self):
        """Test recommendations exclude favorited decks."""
        DeckFavorite.objects.create(user=self.user, deck=self.deck3)
        service = DeckRecommendationService(self.user)
        recommendations = service.get_recommendations()

        self.assertEqual(len(recommendations), 0)

    def test_recommendations_exclude_studied(self):
        """Test recommendations exclude studied decks."""
        flashcard3 = Flashcard.objects.create(
            deck=self.deck3,
            front='Front 3',
            back='Back 3',
        )
        FlashcardProgress.objects.create(
            user=self.user,
            flashcard=flashcard3,
        )
        service = DeckRecommendationService(self.user)
        recommendations = service.get_recommendations()

        self.assertEqual(len(recommendations), 0)


class DeckExportServiceTests(TestCase):
    """Test the deck export service."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.deck = Deck.objects.create(
            name='Test Deck',
            description='Test Description',
            language='en',
            level='A1',
            category='vocabulary',
            owner=self.user,
            is_public=True,
        )
        self.flashcard = Flashcard.objects.create(
            deck=self.deck,
            front='Front',
            back='Back',
            example='Example',
        )

    def test_export_to_json(self):
        """Test exporting deck to JSON."""
        service = DeckExportService(self.deck)
        content = service.export('json')
        data = json.loads(content)

        self.assertEqual(data['name'], self.deck.name)
        self.assertEqual(data['description'], self.deck.description)
        self.assertEqual(len(data['flashcards']), 1)
        self.assertEqual(data['flashcards'][0]['front'], self.flashcard.front)

    def test_export_to_csv(self):
        """Test exporting deck to CSV."""
        service = DeckExportService(self.deck)
        content = service.export('csv')
        lines = content.decode('utf-8').split('\n')

        self.assertEqual(len(lines), 3)  # Header + 1 flashcard + empty line
        self.assertIn('front,back,example', lines[0])
        self.assertIn(self.flashcard.front, lines[1])

    def test_export_invalid_format(self):
        """Test exporting deck with invalid format."""
        service = DeckExportService(self.deck)
        with self.assertRaises(ValueError):
            service.export('invalid')


class DeckImportServiceTests(TestCase):
    """Test the deck import service."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.json_content = json.dumps({
            'name': 'Imported Deck',
            'description': 'Imported Description',
            'language': 'en',
            'level': 'A1',
            'category': 'vocabulary',
            'tags': 'tag1,tag2',
            'flashcards': [
                {
                    'front': 'Front 1',
                    'back': 'Back 1',
                    'example': 'Example 1',
                },
                {
                    'front': 'Front 2',
                    'back': 'Back 2',
                    'example': 'Example 2',
                },
            ],
        })
        self.csv_content = (
            'front,back,example\n'
            'Front 1,Back 1,Example 1\n'
            'Front 2,Back 2,Example 2\n'
        ).encode('utf-8')

    def test_import_from_json(self):
        """Test importing deck from JSON."""
        service = DeckImportService(self.user)
        deck = service.import_deck(self.json_content, 'json')

        self.assertEqual(deck.name, 'Imported Deck')
        self.assertEqual(deck.description, 'Imported Description')
        self.assertEqual(deck.flashcards.count(), 2)

    def test_import_from_csv(self):
        """Test importing deck from CSV."""
        service = DeckImportService(self.user)
        deck = service.import_deck(self.csv_content, 'csv')

        self.assertEqual(deck.name, 'Deck Importado')
        self.assertEqual(deck.flashcards.count(), 2)

    def test_import_invalid_json(self):
        """Test importing deck with invalid JSON."""
        service = DeckImportService(self.user)
        with self.assertRaises(ValueError):
            service.import_deck('invalid json', 'json')

    def test_import_invalid_csv(self):
        """Test importing deck with invalid CSV."""
        service = DeckImportService(self.user)
        with self.assertRaises(ValueError):
            service.import_deck(b'invalid,csv', 'csv') 