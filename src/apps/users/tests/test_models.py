"""Tests for users models."""

from django.contrib.auth import get_user_model
from django.test import TestCase

User = get_user_model()


class UserModelTests(TestCase):
    """Test cases for User model."""

    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
        }
        self.user = User.objects.create_user(**self.user_data)

    def test_create_user(self):
        """Test creating a new user."""
        self.assertEqual(self.user.username, self.user_data['username'])
        self.assertEqual(self.user.email, self.user_data['email'])
        self.assertEqual(self.user.first_name, self.user_data['first_name'])
        self.assertEqual(self.user.last_name, self.user_data['last_name'])
        self.assertTrue(self.user.check_password(self.user_data['password']))
        self.assertFalse(self.user.is_staff)
        self.assertFalse(self.user.is_superuser)
        self.assertTrue(self.user.is_active)

    def test_user_str(self):
        """Test string representation of user."""
        expected = f'{self.user.first_name} {self.user.last_name}'
        self.assertEqual(str(self.user), expected)

    def test_user_get_full_name(self):
        """Test get_full_name() method."""
        expected = f'{self.user.first_name} {self.user.last_name}'
        self.assertEqual(self.user.get_full_name(), expected)

    def test_user_get_short_name(self):
        """Test get_short_name() method."""
        self.assertEqual(self.user.get_short_name(), self.user.first_name)

    def test_user_get_avatar_url(self):
        """Test get_avatar_url() method."""
        self.assertIsNone(self.user.get_avatar_url())

    def test_user_add_experience(self):
        """Test add_experience() method."""
        initial_exp = self.user.experience
        exp_to_add = 100
        self.user.add_experience(exp_to_add)
        self.assertEqual(self.user.experience, initial_exp + exp_to_add) 