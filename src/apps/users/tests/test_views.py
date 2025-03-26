"""Tests for users views."""

from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()


class UserViewSetTests(APITestCase):
    """Test cases for UserViewSet."""

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
        self.user = User.objects.create_user(
            username='existinguser',
            email='existing@example.com',
            password='existingpass123',
        )

    def test_create_user(self):
        """Test creating a new user."""
        url = reverse('users:user-list')
        response = self.client.post(url, self.user_data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)
        self.assertEqual(response.data['username'], self.user_data['username'])
        self.assertEqual(response.data['email'], self.user_data['email'])

    def test_list_users(self):
        """Test listing users."""
        url = reverse('users:user-list')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_retrieve_user(self):
        """Test retrieving a user."""
        url = reverse('users:user-detail', args=[self.user.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_update_user(self):
        """Test updating a user."""
        url = reverse('users:user-detail', args=[self.user.id])
        self.client.force_authenticate(user=self.user)
        data = {'first_name': 'Updated', 'last_name': 'Name'}
        response = self.client.patch(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['first_name'], data['first_name'])
        self.assertEqual(response.data['last_name'], data['last_name'])

    def test_delete_user(self):
        """Test deleting a user."""
        url = reverse('users:user-detail', args=[self.user.id])
        self.client.force_authenticate(user=self.user)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertEqual(User.objects.count(), 0)

    def test_me_endpoint(self):
        """Test me endpoint."""
        url = reverse('users:user-me')
        self.client.force_authenticate(user=self.user)
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user.username)

    def test_change_password(self):
        """Test changing password."""
        url = reverse('users:user-change-password')
        self.client.force_authenticate(user=self.user)
        data = {
            'old_password': 'existingpass123',
            'new_password': 'newpass123',
            'new_password2': 'newpass123',
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.user.refresh_from_db()
        self.assertTrue(self.user.check_password(data['new_password'])) 