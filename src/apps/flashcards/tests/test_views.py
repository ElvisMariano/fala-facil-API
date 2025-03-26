"""Tests for flashcards views."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from ..models import Deck, Flashcard

User = get_user_model()


class DeckViewSetTests(APITestCase):
    """Test cases for DeckViewSet."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123',
        )
        self.deck = Deck.objects.create(
            name='Test Deck',
            language='en',
            level='A1',
            category='vocabulary',
            owner=self.user,
        )
        self.private_deck = Deck.objects.create(
            name='Private Deck',
            language='en',
            level='A1',
            category='vocabulary',
            owner=self.other_user,
            is_public=False,
        )
        self.deck_data = {
            'name': 'New Deck',
            'description': 'New Description',
            'language': 'en',
            'level': 'A1',
            'category': 'vocabulary',
            'is_public': True,
        }

    def test_list_decks(self):
        """Test listing decks."""
        url = reverse('flashcards:deck-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_deck(self):
        """Test creating a deck."""
        url = reverse('flashcards:deck-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, self.deck_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Deck.objects.count(), 3)
        self.assertEqual(response.data['name'], self.deck_data['name'])

    def test_retrieve_deck(self):
        """Test retrieving a deck."""
        url = reverse('flashcards:deck-detail', args=[self.deck.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], self.deck.name)

    def test_update_deck(self):
        """Test updating a deck."""
        url = reverse('flashcards:deck-detail', args=[self.deck.id])
        self.client.force_authenticate(user=self.user)
        data = {'name': 'Updated Deck'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['name'], data['name'])

    def test_delete_deck(self):
        """Test deleting a deck."""
        url = reverse('flashcards:deck-detail', args=[self.deck.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Deck.objects.count(), 1)

    def test_my_decks(self):
        """Test my_decks endpoint."""
        url = reverse('flashcards:deck-my-decks')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_public_decks(self):
        """Test public_decks endpoint."""
        url = reverse('flashcards:deck-public-decks')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)


class FlashcardViewSetTests(APITestCase):
    """Test cases for FlashcardViewSet."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
        )
        self.other_user = User.objects.create_user(
            username='otheruser',
            email='other@example.com',
            password='otherpass123',
        )
        self.deck = Deck.objects.create(
            name='Test Deck',
            language='en',
            level='A1',
            category='vocabulary',
            owner=self.user,
        )
        self.private_deck = Deck.objects.create(
            name='Private Deck',
            language='en',
            level='A1',
            category='vocabulary',
            owner=self.other_user,
            is_public=False,
        )
        self.flashcard = Flashcard.objects.create(
            deck=self.deck,
            front='Front',
            back='Back',
            example='Example',
        )
        self.private_flashcard = Flashcard.objects.create(
            deck=self.private_deck,
            front='Private Front',
            back='Private Back',
            example='Private Example',
        )
        self.flashcard_data = {
            'deck': self.deck.id,
            'front': 'New Front',
            'back': 'New Back',
            'example': 'New Example',
        }

    def test_list_flashcards(self):
        """Test listing flashcards."""
        url = reverse('flashcards:flashcard-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_create_flashcard(self):
        """Test creating a flashcard."""
        url = reverse('flashcards:flashcard-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.post(url, self.flashcard_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Flashcard.objects.count(), 3)
        self.assertEqual(response.data['front'], self.flashcard_data['front'])

    def test_retrieve_flashcard(self):
        """Test retrieving a flashcard."""
        url = reverse('flashcards:flashcard-detail', args=[self.flashcard.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['front'], self.flashcard.front)

    def test_update_flashcard(self):
        """Test updating a flashcard."""
        url = reverse('flashcards:flashcard-detail', args=[self.flashcard.id])
        self.client.force_authenticate(user=self.user)
        data = {'front': 'Updated Front'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['front'], data['front'])

    def test_delete_flashcard(self):
        """Test deleting a flashcard."""
        url = reverse('flashcards:flashcard-detail', args=[self.flashcard.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(Flashcard.objects.count(), 1)

    def test_my_flashcards(self):
        """Test my_flashcards endpoint."""
        url = reverse('flashcards:flashcard-my-flashcards')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_public_flashcards(self):
        """Test public_flashcards endpoint."""
        url = reverse('flashcards:flashcard-public-flashcards')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1) 