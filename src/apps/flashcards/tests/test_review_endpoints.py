"""Tests for flashcard review endpoints."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient

from ..models import Deck, Flashcard, FlashcardProgress

User = get_user_model()


class FlashcardReviewTests(TestCase):
    """Test the flashcard review endpoints."""

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

    def test_review_flashcard(self):
        """Test reviewing a flashcard."""
        url = reverse('flashcards:flashcard-review', args=[self.flashcard.id])
        data = {
            'quality': 4,
            'response_time': 2.5,
        }
        res = self.client.post(url, data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertTrue(
            FlashcardProgress.objects.filter(
                user=self.user,
                flashcard=self.flashcard,
            ).exists()
        )
        progress = FlashcardProgress.objects.get(
            user=self.user,
            flashcard=self.flashcard,
        )
        self.assertEqual(progress.average_response_time, 2.5)

    def test_review_flashcard_invalid_quality(self):
        """Test reviewing a flashcard with invalid quality."""
        url = reverse('flashcards:flashcard-review', args=[self.flashcard.id])
        data = {
            'quality': 6,  # Invalid quality (should be 0-5)
            'response_time': 2.5,
        }
        res = self.client.post(url, data)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_flashcard_invalid_response_time(self):
        """Test reviewing a flashcard with invalid response time."""
        url = reverse('flashcards:flashcard-review', args=[self.flashcard.id])
        data = {
            'quality': 4,
            'response_time': -1.0,  # Invalid response time (should be >= 0)
        }
        res = self.client.post(url, data)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_review_flashcard_update_existing_progress(self):
        """Test updating existing flashcard progress."""
        # Create initial progress
        progress = FlashcardProgress.objects.create(
            user=self.user,
            flashcard=self.flashcard,
            average_response_time=1.0,
        )

        url = reverse('flashcards:flashcard-review', args=[self.flashcard.id])
        data = {
            'quality': 3,
            'response_time': 3.0,
        }
        res = self.client.post(url, data)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        progress.refresh_from_db()
        self.assertEqual(progress.average_response_time, 2.0)  # (1.0 + 3.0) / 2

    def test_due_review_with_due_cards(self):
        """Test getting due flashcards for review."""
        # Create a flashcard progress with a past review date
        progress = FlashcardProgress.objects.create(
            user=self.user,
            flashcard=self.flashcard,
            next_review_date=timezone.now() - timezone.timedelta(days=1),
        )

        url = reverse('flashcards:flashcard-due-review')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['flashcard']['id'], self.flashcard.id)

    def test_due_review_with_no_due_cards(self):
        """Test getting due flashcards when none are due."""
        # Create a flashcard progress with a future review date
        progress = FlashcardProgress.objects.create(
            user=self.user,
            flashcard=self.flashcard,
            next_review_date=timezone.now() + timezone.timedelta(days=1),
        )

        url = reverse('flashcards:flashcard-due-review')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        # The implementation might return an empty list when no cards are due
        # and all cards have progress records
        self.assertEqual(len(res.data), 0)

    def test_due_review_with_no_progress(self):
        """Test getting due flashcards when no progress exists."""
        url = reverse('flashcards:flashcard-due-review')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)  # Should return new cards
        self.assertEqual(res.data[0]['id'], self.flashcard.id)

    def test_progress_endpoint(self):
        """Test getting user's flashcard progress."""
        # Create flashcard progress
        progress = FlashcardProgress.objects.create(
            user=self.user,
            flashcard=self.flashcard,
            correct_attempts=5,
            incorrect_attempts=2,
        )

        url = reverse('flashcards:flashcard-progress')
        res = self.client.get(url)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['flashcard']['id'], self.flashcard.id)
        self.assertEqual(res.data[0]['correct_attempts'], 5)
        self.assertEqual(res.data[0]['incorrect_attempts'], 2)