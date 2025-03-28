"""Tests for flashcards views."""

import json
from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from ..models import Deck, DeckFavorite, Flashcard

User = get_user_model()


class DeckViewSetTests(TestCase):
    """Test the deck viewset."""

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
            description='Test Description',
            language='en',
            level='A1',
            category='vocabulary',
            owner=self.user,
            is_public=True,
        )

        self.flashcard = Flashcard.objects.create(
            deck=self.deck,
            front='Test Front',
            back='Test Back',
            example='Test Example',
        )

    def test_recommendations(self):
        """Test getting deck recommendations."""
        url = reverse('flashcards:deck-recommendations')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIsInstance(res.data, list)

    def test_export_deck_json(self):
        """Test exporting deck to JSON."""
        url = reverse('flashcards:deck-export', args=[self.deck.id])
        res = self.client.get(url, {'format': 'json'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res['Content-Type'], 'application/json')
        data = json.loads(res.content)
        self.assertEqual(data['name'], self.deck.name)
        self.assertEqual(len(data['flashcards']), 1)

    def test_export_deck_csv(self):
        """Test exporting deck to CSV."""
        url = reverse('flashcards:deck-export', args=[self.deck.id])
        res = self.client.get(url, {'format': 'csv'})

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res['Content-Type'], 'text/csv')
        content = res.content.decode('utf-8')
        self.assertIn('front,back,example', content)
        self.assertIn(self.flashcard.front, content)

    def test_import_deck_json(self):
        """Test importing deck from JSON."""
        url = reverse('flashcards:deck-import-deck')
        content = {
            'name': 'Imported Deck',
            'description': 'Imported Description',
            'language': 'en',
            'level': 'A1',
            'category': 'vocabulary',
            'flashcards': [
                {
                    'front': 'Front 1',
                    'back': 'Back 1',
                    'example': 'Example 1',
                },
            ],
        }
        json_file = json.dumps(content).encode('utf-8')
        res = self.client.post(
            url,
            {'file': ('deck.json', json_file, 'application/json')},
            format='multipart',
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Deck.objects.count(), 2)
        self.assertEqual(Flashcard.objects.count(), 2)

    def test_import_deck_csv(self):
        """Test importing deck from CSV."""
        url = reverse('flashcards:deck-import-deck')
        content = (
            'front,back,example\n'
            'Front 1,Back 1,Example 1\n'
        ).encode('utf-8')
        res = self.client.post(
            url,
            {'file': ('deck.csv', content, 'text/csv')},
            format='multipart',
        )

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Deck.objects.count(), 2)
        self.assertEqual(Flashcard.objects.count(), 2)

    def test_import_deck_no_file(self):
        """Test importing deck without file."""
        url = reverse('flashcards:deck-import-deck')
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_import_deck_invalid_format(self):
        """Test importing deck with invalid format."""
        url = reverse('flashcards:deck-import-deck')
        content = b'invalid content'
        res = self.client.post(
            url,
            {'file': ('deck.txt', content, 'text/plain')},
            format='multipart',
        )

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_duplicate_deck(self):
        """Test duplicating a deck."""
        url = reverse('flashcards:deck-duplicate', args=[self.deck.id])
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Deck.objects.count(), 2)
        new_deck = Deck.objects.exclude(id=self.deck.id).first()
        self.assertEqual(new_deck.name, f'Cópia de {self.deck.name}')
        self.assertEqual(new_deck.flashcards.count(), 1)

    def test_archive_deck(self):
        """Test archiving a deck."""
        url = reverse('flashcards:deck-archive', args=[self.deck.id])
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.deck.refresh_from_db()
        self.assertTrue(self.deck.is_archived)
        self.assertFalse(self.deck.is_public)
        self.assertFalse(self.deck.is_featured)

    def test_unarchive_deck(self):
        """Test unarchiving a deck."""
        self.deck.archive()
        url = reverse('flashcards:deck-unarchive', args=[self.deck.id])
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.deck.refresh_from_db()
        self.assertFalse(self.deck.is_archived)

    def test_share_deck(self):
        """Test sharing a deck."""
        url = reverse('flashcards:deck-share', args=[self.deck.id])
        initial_share_count = self.deck.share_count
        res = self.client.post(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.deck.refresh_from_db()
        self.assertEqual(self.deck.share_count, initial_share_count + 1)

    def test_my_decks(self):
        """Test retrieving user's decks."""
        url = reverse('flashcards:deck-my-decks')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], self.deck.id)

    def test_public_decks(self):
        """Test retrieving public decks."""
        url = reverse('flashcards:deck-public-decks')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], self.deck.id)

    def test_featured_decks(self):
        """Test retrieving featured decks."""
        self.deck.is_featured = True
        self.deck.save()
        url = reverse('flashcards:deck-featured')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], self.deck.id)

    def test_archived_decks(self):
        """Test retrieving archived decks."""
        self.deck.archive()
        url = reverse('flashcards:deck-archived')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['id'], self.deck.id)


class DeckFavoriteViewSetTests(TestCase):
    """Test the deck favorite viewset."""

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
            description='Test Description',
            language='en',
            level='A1',
            category='vocabulary',
            owner=self.user,
            is_public=True,
        )

    def test_favorite_deck(self):
        """Test favoriting a deck."""
        url = reverse('flashcards:favorite-list')
        res = self.client.post(url, {'deck_id': self.deck.id})

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            DeckFavorite.objects.filter(
                user=self.user,
                deck=self.deck,
            ).exists()
        )
        self.deck.refresh_from_db()
        self.assertEqual(self.deck.favorite_count, 1)

    def test_unfavorite_deck(self):
        """Test unfavoriting a deck."""
        favorite = DeckFavorite.objects.create(
            user=self.user,
            deck=self.deck,
        )
        url = reverse('flashcards:favorite-detail', args=[favorite.id])
        res = self.client.delete(url)

        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            DeckFavorite.objects.filter(
                user=self.user,
                deck=self.deck,
            ).exists()
        )
        self.deck.refresh_from_db()
        self.assertEqual(self.deck.favorite_count, 0)

    def test_list_favorites(self):
        """Test listing favorite decks."""
        DeckFavorite.objects.create(
            user=self.user,
            deck=self.deck,
        )
        url = reverse('flashcards:favorite-list')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['deck']['id'], self.deck.id)


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