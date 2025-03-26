"""Tests for flashcards models."""

from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Deck, Flashcard

User = get_user_model()


class DeckModelTests(TestCase):
    """Test cases for Deck model."""

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
        )

    def test_deck_str(self):
        """Test deck string representation."""
        self.assertEqual(str(self.deck), 'Test Deck')

    def test_deck_fields(self):
        """Test deck fields."""
        self.assertEqual(self.deck.name, 'Test Deck')
        self.assertEqual(self.deck.description, 'Test Description')
        self.assertEqual(self.deck.language, 'en')
        self.assertEqual(self.deck.level, 'A1')
        self.assertEqual(self.deck.category, 'vocabulary')
        self.assertEqual(self.deck.owner, self.user)
        self.assertTrue(self.deck.is_public)
        self.assertIsNotNone(self.deck.created_at)
        self.assertIsNotNone(self.deck.updated_at)

    def test_deck_ordering(self):
        """Test deck ordering."""
        deck2 = Deck.objects.create(
            name='Another Deck',
            language='en',
            level='A1',
            category='vocabulary',
            owner=self.user,
        )
        decks = Deck.objects.all()
        self.assertEqual(decks[0], deck2)  # Another Deck comes first alphabetically
        self.assertEqual(decks[1], self.deck)  # Test Deck comes second

    def test_deck_flashcards_count(self):
        """Test deck flashcards count."""
        Flashcard.objects.create(
            deck=self.deck,
            front='Front',
            back='Back',
            example='Example',
        )
        Flashcard.objects.create(
            deck=self.deck,
            front='Front 2',
            back='Back 2',
            example='Example 2',
        )
        self.assertEqual(self.deck.flashcards.count(), 2)


class FlashcardModelTests(TestCase):
    """Test cases for Flashcard model."""

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

    def test_flashcard_str(self):
        """Test flashcard string representation."""
        self.assertEqual(str(self.flashcard), 'Front - Back')

    def test_flashcard_fields(self):
        """Test flashcard fields."""
        self.assertEqual(self.flashcard.deck, self.deck)
        self.assertEqual(self.flashcard.front, 'Front')
        self.assertEqual(self.flashcard.back, 'Back')
        self.assertEqual(self.flashcard.example, 'Example')
        self.assertIsNotNone(self.flashcard.created_at)
        self.assertIsNotNone(self.flashcard.updated_at)

    def test_flashcard_ordering(self):
        """Test flashcard ordering."""
        flashcard2 = Flashcard.objects.create(
            deck=self.deck,
            front='Another Front',
            back='Another Back',
            example='Another Example',
        )
        flashcards = Flashcard.objects.all()
        self.assertEqual(flashcards[0], flashcard2)  # Another Front comes first alphabetically
        self.assertEqual(flashcards[1], self.flashcard)  # Front comes second

    def test_flashcard_deck_relationship(self):
        """Test flashcard-deck relationship."""
        self.assertEqual(self.flashcard.deck, self.deck)
        self.assertIn(self.flashcard, self.deck.flashcards.all())

    def test_get_audio_url(self):
        """Test get_audio_url() method."""
        self.assertIsNone(self.flashcard.get_audio_url())

    def test_get_image_url(self):
        """Test get_image_url() method."""
        self.assertIsNone(self.flashcard.get_image_url()) 