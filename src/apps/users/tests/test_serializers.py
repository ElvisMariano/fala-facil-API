"""Tests for users serializers."""

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.exceptions import ValidationError

from ..serializers import (ChangePasswordSerializer, UserSerializer,
                         UserUpdateSerializer)

User = get_user_model()


class UserSerializerTests(TestCase):
    """Test cases for UserSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password': 'testpass123',
            'password2': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User',
        }

    def test_create_user(self):
        """Test creating a new user."""
        serializer = UserSerializer(data=self.user_data)
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.username, self.user_data['username'])
        self.assertEqual(user.email, self.user_data['email'])
        self.assertEqual(user.first_name, self.user_data['first_name'])
        self.assertEqual(user.last_name, self.user_data['last_name'])
        self.assertTrue(user.check_password(self.user_data['password']))

    def test_password_validation(self):
        """Test password validation."""
        data = self.user_data.copy()
        data['password2'] = 'wrongpass'
        serializer = UserSerializer(data=data)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)


class UserUpdateSerializerTests(TestCase):
    """Test cases for UserUpdateSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
        )
        self.update_data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'bio': 'Test bio',
        }

    def test_update_user(self):
        """Test updating a user."""
        serializer = UserUpdateSerializer(
            instance=self.user,
            data=self.update_data,
            partial=True,
        )
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertEqual(user.first_name, self.update_data['first_name'])
        self.assertEqual(user.last_name, self.update_data['last_name'])
        self.assertEqual(user.bio, self.update_data['bio'])


class ChangePasswordSerializerTests(TestCase):
    """Test cases for ChangePasswordSerializer."""

    def setUp(self):
        """Set up test data."""
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='oldpass123',
        )
        self.context = {'request': type('Request', (), {'user': self.user})}
        self.password_data = {
            'old_password': 'oldpass123',
            'new_password': 'newpass123',
            'new_password2': 'newpass123',
        }

    def test_change_password(self):
        """Test changing password."""
        serializer = ChangePasswordSerializer(
            data=self.password_data,
            context=self.context,
        )
        self.assertTrue(serializer.is_valid())
        user = serializer.save()
        self.assertTrue(user.check_password(self.password_data['new_password']))

    def test_wrong_old_password(self):
        """Test validation with wrong old password."""
        data = self.password_data.copy()
        data['old_password'] = 'wrongpass'
        serializer = ChangePasswordSerializer(data=data, context=self.context)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True)

    def test_password_mismatch(self):
        """Test validation with mismatched new passwords."""
        data = self.password_data.copy()
        data['new_password2'] = 'differentpass'
        serializer = ChangePasswordSerializer(data=data, context=self.context)
        with self.assertRaises(ValidationError):
            serializer.is_valid(raise_exception=True) 