"""Tests for flashcard and deck creation endpoints."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from ..models import Deck, Flashcard

User = get_user_model()


class DeckCreationTests(TestCase):
    """Test the deck creation endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)

        self.deck_data = {
            'name': 'Test Deck',
            'description': 'Test Description',
            'language': 'en',
            'level': 'A1',
            'category': 'vocabulary',
            'is_public': True,
        }

    def test_create_deck(self):
        """Test creating a deck."""
        url = reverse('flashcards:deck-list')
        response = self.client.post(url, self.deck_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Deck.objects.count(), 1)
        deck = Deck.objects.first()
        self.assertEqual(deck.name, self.deck_data['name'])
        self.assertEqual(deck.description, self.deck_data['description'])
        self.assertEqual(deck.language, self.deck_data['language'])
        self.assertEqual(deck.level, self.deck_data['level'])
        self.assertEqual(deck.category, self.deck_data['category'])
        self.assertEqual(deck.is_public, self.deck_data['is_public'])
        self.assertEqual(deck.owner, self.user)

    def test_create_deck_missing_required_fields(self):
        """Test creating a deck with missing required fields."""
        url = reverse('flashcards:deck-list')
        # Remove required field 'name'
        invalid_data = self.deck_data.copy()
        invalid_data.pop('name')

        response = self.client.post(url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Deck.objects.count(), 0)
        self.assertIn('name', response.data)

    def test_create_deck_invalid_language(self):
        """Test creating a deck with invalid language."""
        url = reverse('flashcards:deck-list')
        invalid_data = self.deck_data.copy()
        invalid_data['language'] = 'invalid_language'

        response = self.client.post(url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Deck.objects.count(), 0)
        self.assertIn('language', response.data)

    def test_create_deck_invalid_level(self):
        """Test creating a deck with invalid level."""
        url = reverse('flashcards:deck-list')
        invalid_data = self.deck_data.copy()
        invalid_data['level'] = 'invalid_level'

        response = self.client.post(url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Deck.objects.count(), 0)
        self.assertIn('level', response.data)

    def test_create_deck_invalid_category(self):
        """Test creating a deck with invalid category."""
        url = reverse('flashcards:deck-list')
        invalid_data = self.deck_data.copy()
        invalid_data['category'] = 'invalid_category'

        response = self.client.post(url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Deck.objects.count(), 0)
        self.assertIn('category', response.data)

    def test_create_deck_unauthenticated(self):
        """Test creating a deck when unauthenticated."""
        self.client.force_authenticate(user=None)
        url = reverse('flashcards:deck-list')

        response = self.client.post(url, self.deck_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Deck.objects.count(), 0)


class FlashcardCreationTests(TestCase):
    """Test the flashcard creation endpoints."""

    def setUp(self):
        """Set up test data."""
        self.client = APIClient()
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.client.force_authenticate(user=self.user)

        self.deck = Deck.objects.create(
            name='Test Deck',
            language='en',
            level='A1',
            category='vocabulary',
            owner=self.user,
        )

        self.flashcard_data = {
            'deck': self.deck.id,
            'front': 'Test Front',
            'back': 'Test Back',
            'example': 'Test Example',
        }

    def test_create_flashcard(self):
        """Test creating a flashcard."""
        url = reverse('flashcards:flashcard-list')
        response = self.client.post(url, self.flashcard_data)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Flashcard.objects.count(), 1)
        flashcard = Flashcard.objects.first()
        self.assertEqual(flashcard.deck, self.deck)
        self.assertEqual(flashcard.front, self.flashcard_data['front'])
        self.assertEqual(flashcard.back, self.flashcard_data['back'])
        self.assertEqual(flashcard.example, self.flashcard_data['example'])

    def test_create_flashcard_missing_required_fields(self):
        """Test creating a flashcard with missing required fields."""
        url = reverse('flashcards:flashcard-list')
        # Remove required field 'front'
        invalid_data = self.flashcard_data.copy()
        invalid_data.pop('front')

        response = self.client.post(url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Flashcard.objects.count(), 0)
        self.assertIn('front', response.data)

    def test_create_flashcard_without_deck(self):
        """Test creating a flashcard without specifying a deck."""
        url = reverse('flashcards:flashcard-list')
        invalid_data = self.flashcard_data.copy()
        invalid_data.pop('deck')

        response = self.client.post(url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Flashcard.objects.count(), 0)
        self.assertIn('deck', response.data)

    def test_create_flashcard_invalid_deck(self):
        """Test creating a flashcard with an invalid deck ID."""
        url = reverse('flashcards:flashcard-list')
        invalid_data = self.flashcard_data.copy()
        invalid_data['deck'] = 999  # Non-existent deck ID

        response = self.client.post(url, invalid_data)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Flashcard.objects.count(), 0)
        self.assertIn('deck', response.data)

    def test_create_flashcard_other_user_deck(self):
        """Test creating a flashcard in another user's deck."""
        other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123',
        )
        other_deck = Deck.objects.create(
            name='Other Deck',
            language='en',
            level='A1',
            category='vocabulary',
            owner=other_user,
        )

        url = reverse('flashcards:flashcard-list')
        invalid_data = self.flashcard_data.copy()
        invalid_data['deck'] = other_deck.id

        response = self.client.post(url, invalid_data)

        # Should fail because user doesn't own the deck
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Flashcard.objects.count(), 0)

    def test_create_flashcard_unauthenticated(self):
        """Test creating a flashcard when unauthenticated."""
        self.client.force_authenticate(user=None)
        url = reverse('flashcards:flashcard-list')

        response = self.client.post(url, self.flashcard_data)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(Flashcard.objects.count(), 0)

    def test_create_multiple_flashcards(self):
        """Test creating multiple flashcards in the same deck."""
        url = reverse('flashcards:flashcard-list')

        # Create first flashcard
        response1 = self.client.post(url, self.flashcard_data)
        self.assertEqual(response1.status_code, status.HTTP_201_CREATED)

        # Create second flashcard
        flashcard_data2 = {
            'deck': self.deck.id,
            'front': 'Second Front',
            'back': 'Second Back',
            'example': 'Second Example',
        }
        response2 = self.client.post(url, flashcard_data2)
        self.assertEqual(response2.status_code, status.HTTP_201_CREATED)

        # Verify both flashcards were created
        self.assertEqual(Flashcard.objects.count(), 2)
        self.assertEqual(self.deck.flashcards.count(), 2)