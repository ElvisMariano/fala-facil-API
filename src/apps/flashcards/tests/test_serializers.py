"""Tests for flashcards serializers."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Deck, Flashcard
from ..serializers import DeckDetailSerializer, DeckSerializer, FlashcardSerializer

User = get_user_model()


class FlashcardSerializerTests(TestCase):
    """Test cases for FlashcardSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.deck = Deck.objects.create(
            name='Test Deck',
            language='en',
            level='A1',
            category='vocabulary',
            owner=self.user,
        )
        self.flashcard_data = {
            'deck': self.deck.id,
            'front': 'Front',
            'back': 'Back',
            'example': 'Example',
        }

    def test_valid_flashcard_data(self):
        """Test serializer with valid data."""
        serializer = FlashcardSerializer(data=self.flashcard_data)
        self.assertTrue(serializer.is_valid())

    def test_create_flashcard(self):
        """Test creating a flashcard with serializer."""
        serializer = FlashcardSerializer(data=self.flashcard_data)
        self.assertTrue(serializer.is_valid())
        flashcard = serializer.save()
        self.assertEqual(flashcard.deck, self.deck)
        self.assertEqual(flashcard.front, self.flashcard_data['front'])
        self.assertEqual(flashcard.back, self.flashcard_data['back'])
        self.assertEqual(flashcard.example, self.flashcard_data['example'])


class DeckSerializerTests(TestCase):
    """Test cases for DeckSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.deck_data = {
            'name': 'Test Deck',
            'description': 'Test Description',
            'language': 'en',
            'level': 'A1',
            'category': 'vocabulary',
            'is_public': True,
        }
        self.context = {'request': type('Request', (), {'user': self.user})}

    def test_valid_deck_data(self):
        """Test serializer with valid data."""
        serializer = DeckSerializer(data=self.deck_data, context=self.context)
        self.assertTrue(serializer.is_valid())

    def test_create_deck(self):
        """Test creating a deck with serializer."""
        serializer = DeckSerializer(data=self.deck_data, context=self.context)
        self.assertTrue(serializer.is_valid())
        deck = serializer.save()
        self.assertEqual(deck.name, self.deck_data['name'])
        self.assertEqual(deck.description, self.deck_data['description'])
        self.assertEqual(deck.language, self.deck_data['language'])
        self.assertEqual(deck.level, self.deck_data['level'])
        self.assertEqual(deck.category, self.deck_data['category'])
        self.assertEqual(deck.is_public, self.deck_data['is_public'])
        self.assertEqual(deck.owner, self.user)


class DeckDetailSerializerTests(TestCase):
    """Test cases for DeckDetailSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.deck = Deck.objects.create(
            name='Test Deck',
            language='en',
            level='A1',
            category='vocabulary',
            owner=self.user,
        )
        self.flashcard = Flashcard.objects.create(
            deck=self.deck,
            front='Front',
            back='Back',
            example='Example',
        )

    def test_deck_detail_serializer(self):
        """Test DeckDetailSerializer."""
        serializer = DeckDetailSerializer(self.deck)
        data = serializer.data
        self.assertEqual(data['name'], self.deck.name)
        self.assertEqual(data['language'], self.deck.language)
        self.assertEqual(data['level'], self.deck.level)
        self.assertEqual(data['category'], self.deck.category)
        self.assertEqual(data['owner'], self.user.id)
        self.assertEqual(data['owner_username'], self.user.username)
        self.assertEqual(data['flashcards_count'], 1)
        self.assertEqual(len(data['flashcards']), 1)
        self.assertEqual(data['flashcards'][0]['front'], self.flashcard.front)
        self.assertEqual(data['flashcards'][0]['back'], self.flashcard.back)
        self.assertEqual(data['flashcards'][0]['example'], self.flashcard.example) 