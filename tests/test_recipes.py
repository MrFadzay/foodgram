from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User


class RecipeAPITests(TestCase):
    def setUp(self):
        self.client = APIClient()
        self.user = User.objects.create_user(
            email='test@example.com',
            username='testuser',
            password='testpass123',
            first_name='Test',
            last_name='User'
        )
        self.client.force_authenticate(user=self.user)

        # Создаем тестовые данные
        self.tag = Tag.objects.create(
            name='Завтрак',
            color='#E26C2D',
            slug='breakfast'
        )
        self.ingredient = Ingredient.objects.create(
            name='Яйцо',
            measurement_unit='шт.'
        )
        self.recipe_data = {
            'name': 'Тестовый рецепт',
            'text': 'Описание тестового рецепта',
            'cooking_time': 30,
            'tags': [self.tag.id],
            'ingredients': [{'id': self.ingredient.id, 'amount': 2}],
            'image': 'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+P+/HgAFhAJ/wlseKgAAAABJRU5ErkJggg=='
        }

    def test_create_recipe(self):
        """Тест создания рецепта."""
        url = reverse('api:v1:recipes-list')
        response = self.client.post(url, self.recipe_data, format='json')
        # Добавляем вывод ответа для отладки
        print("Response data:", response.data)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Recipe.objects.count(), 1)
        recipe = Recipe.objects.first()
        self.assertEqual(recipe.name, self.recipe_data['name'])
        self.assertEqual(recipe.author, self.user)
        self.assertEqual(recipe.ingredients.count(), 1)

    def test_get_recipe_list(self):
        """Тест получения списка рецептов."""
        recipe = Recipe.objects.create(
            author=self.user,
            name='Тестовый рецепт',
            text='Описание',
            cooking_time=30
        )
        url = reverse('api:v1:recipes-list')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_filter_recipes_by_tag(self):
        """Тест фильтрации рецептов по тегу."""
        recipe = Recipe.objects.create(
            author=self.user,
            name='Тестовый рецепт',
            text='Описание',
            cooking_time=30
        )
        recipe.tags.add(self.tag)

        url = reverse('api:v1:recipes-list')
        response = self.client.get(url, {'tags': self.tag.slug})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data['results']), 1)

    def test_favorite_recipe(self):
        """Тест добавления рецепта в избранное."""
        recipe = Recipe.objects.create(
            author=self.user,
            name='Тестовый рецепт',
            text='Описание',
            cooking_time=30
        )
        url = reverse('api:v1:recipes-favorite', args=[recipe.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            recipe.favorites.filter(user=self.user).exists()
        )

    def test_shopping_cart(self):
        """Тест добавления рецепта в список покупок."""
        recipe = Recipe.objects.create(
            author=self.user,
            name='Тестовый рецепт',
            text='Описание',
            cooking_time=30
        )
        url = reverse('api:v1:recipes-shopping-cart', args=[recipe.id])
        response = self.client.post(url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(
            recipe.shopping_cart.filter(user=self.user).exists()
        )

    def test_download_shopping_cart(self):
        """Тест скачивания списка покупок."""
        recipe = Recipe.objects.create(
            author=self.user,
            name='Тестовый рецепт',
            text='Описание',
            cooking_time=30
        )
        RecipeIngredient.objects.create(
            recipe=recipe,
            ingredient=self.ingredient,
            amount=2
        )

        # Добавляем рецепт в список покупок
        url = reverse('api:v1:recipes-shopping-cart', args=[recipe.id])
        self.client.post(url)

        # Скачиваем список покупок
        url = reverse('api:v1:recipes-download-shopping-cart')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response['Content-Type'], 'text/plain; charset=utf-8')
