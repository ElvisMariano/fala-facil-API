"""Tests for flashcards admin."""

from django.contrib.admin.sites import AdminSite
from django.contrib.auth import get_user_model
from django.test import TestCase

from ..admin import DeckAdmin, FlashcardAdmin
from ..models import Deck, Flashcard

User = get_user_model()


class DeckAdminTests(TestCase):
    """Test cases for DeckAdmin."""

    def setUp(self):
        """Set up test data."""
        self.site = AdminSite()
        self.deck_admin = DeckAdmin(Deck, self.site)
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

    def test_list_display(self):
        """Test list display fields."""
        self.assertEqual(
            self.deck_admin.list_display,
            ('name', 'language', 'level', 'category', 'owner', 'is_public', 'created_at', 'updated_at'),
        )

    def test_list_filter(self):
        """Test list filter fields."""
        self.assertEqual(
            self.deck_admin.list_filter,
            ('language', 'level', 'category', 'is_public', 'created_at', 'updated_at'),
        )

    def test_search_fields(self):
        """Test search fields."""
        self.assertEqual(
            self.deck_admin.search_fields,
            ('name', 'description', 'owner__username', 'owner__email'),
        )

    def test_readonly_fields(self):
        """Test readonly fields."""
        self.assertEqual(
            self.deck_admin.readonly_fields,
            ('created_at', 'updated_at'),
        )


class FlashcardAdminTests(TestCase):
    """Test cases for FlashcardAdmin."""

    def setUp(self):
        """Set up test data."""
        self.site = AdminSite()
        self.flashcard_admin = FlashcardAdmin(Flashcard, self.site)
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

    def test_list_display(self):
        """Test list display fields."""
        self.assertEqual(
            self.flashcard_admin.list_display,
            ('front', 'back', 'deck', 'created_at', 'updated_at'),
        )

    def test_list_filter(self):
        """Test list filter fields."""
        self.assertEqual(
            self.flashcard_admin.list_filter,
            ('deck', 'created_at', 'updated_at'),
        )

    def test_search_fields(self):
        """Test search fields."""
        self.assertEqual(
            self.flashcard_admin.search_fields,
            ('front', 'back', 'example', 'deck__name'),
        )

    def test_readonly_fields(self):
        """Test readonly fields."""
        self.assertEqual(
            self.flashcard_admin.readonly_fields,
            ('created_at', 'updated_at'),
        ) 