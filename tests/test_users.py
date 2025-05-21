from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from users.models import User


class UserAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'email': 'test@example.com',
            'username': 'testuser',
            'password': 'testpass123',
            'first_name': 'Test',
            'last_name': 'User'
        }
        self.user = User.objects.create_user(**self.user_data)
        self.client.force_authenticate(user=self.user)

    def test_create_user(self):
        """Тест создания пользователя."""
        url = reverse('api:v1:users-list')
        new_user_data = {
            'email': 'new@example.com',
            'username': 'newuser',
            'password': 'newpass123',
            'first_name': 'New',
            'last_name': 'User'
        }
        response = self.client.post(url, new_user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(User.objects.count(), 2)

    def test_get_user_list(self):
        """Тест получения списка пользователей."""
        url = reverse('api:v1:users-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_get_current_user(self):
        """Тест получения текущего пользователя."""
        url = reverse('api:v1:users-me')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email'], self.user_data['email'])

    def test_follow_user(self):
        """Тест подписки на пользователя."""
        author = User.objects.create_user(
            email='author@example.com',
            username='author',
            password='authorpass123',
            first_name='Author',
            last_name='Test'
        )
        url = reverse('api:v1:users-subscribe', args=[author.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            author.following.filter(user=self.user).exists()
        )

    def test_unfollow_user(self):
        """Тест отписки от пользователя."""
        author = User.objects.create_user(
            email='author@example.com',
            username='author',
            password='authorpass123',
            first_name='Author',
            last_name='Test'
        )
        url = reverse('api:v1:users-subscribe', args=[author.id])
        # Сначала подписываемся
        self.client.post(url)
        # Затем отписываемся
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(
            author.following.filter(user=self.user).exists()
        )

    def test_get_subscriptions(self):
        """Тест получения списка подписок."""
        author = User.objects.create_user(
            email='author@example.com',
            username='author',
            password='authorpass123',
            first_name='Author',
            last_name='Test'
        )
        url = reverse('api:v1:users-subscribe', args=[author.id])
        self.client.post(url)

        subscriptions_url = reverse('api:v1:users-subscriptions')
        response = self.client.get(subscriptions_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)
