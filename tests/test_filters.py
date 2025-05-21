import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from recipes.models import Ingredient, Recipe, Tag
from users.models import User


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def user():
    return User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='testpass123'
    )


@pytest.fixture
def tag():
    return Tag.objects.create(
        name='Завтрак',
        color='#FF0000',
        slug='breakfast'
    )


@pytest.fixture
def ingredient():
    return Ingredient.objects.create(
        name='Яйцо',
        measurement_unit='шт.'
    )


@pytest.fixture
def recipe(user, tag, ingredient):
    recipe = Recipe.objects.create(
        author=user,
        name='Тестовый рецепт',
        text='Описание тестового рецепта',
        cooking_time=30
    )
    recipe.tags.add(tag)
    return recipe


@pytest.mark.django_db
class TestFilters:
    def test_recipe_tag_filter(self, api_client, recipe, tag):
        """Тест фильтрации рецептов по тегам."""
        url = reverse('api:v1:recipes-list')
        response = api_client.get(url, {'tags': tag.slug})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == recipe.name

    def test_recipe_author_filter(self, api_client, recipe, user):
        """Тест фильтрации рецептов по автору."""
        url = reverse('api:v1:recipes-list')
        response = api_client.get(url, {'author': user.id})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data['results']) == 1
        assert response.data['results'][0]['name'] == recipe.name

    def test_ingredient_search(self, api_client, ingredient):
        """Тест поиска ингредиентов."""
        url = reverse('api:v1:ingredients-list')
        response = api_client.get(url, {'name': 'Яй'})

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]['name'] == ingredient.name


@pytest.mark.django_db
class TestErrorHandling:
    def test_invalid_tag_color(self, api_client, user):
        """Тест обработки ошибки при создании тега с невалидным цветом."""
        api_client.force_authenticate(user=user)
        url = reverse('api:v1:tags-list')
        data = {
            'name': 'Test',
            'color': 'invalid-color',
            'slug': 'test'
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'color' in response.data

    def test_invalid_recipe_cooking_time(self, api_client, user):
        """
        Тест обработки ошибки при создании рецепта
        с невалидным временем приготовления.
        """
        api_client.force_authenticate(user=user)
        url = reverse('api:v1:recipes-list')
        data = {
            'name': 'Test Recipe',
            'text': 'Test description',
            'cooking_time': 0,
            'ingredients': [],
            'tags': []
        }
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'cooking_time' in response.data

    def test_duplicate_favorite(self, api_client, user, recipe):
        """Тест обработки ошибки при повторном добавлении в избранное."""
        api_client.force_authenticate(user=user)
        url = reverse('api:v1:recipes-favorite', kwargs={'pk': recipe.id})

        # Первое добавление
        response = api_client.post(url)
        assert response.status_code == status.HTTP_201_CREATED

        # Повторное добавление
        response = api_client.post(url)
        assert response.status_code == status.HTTP_400_BAD_REQUEST
        assert 'errors' in response.data

    def test_unauthorized_access(self, api_client, recipe):
        """Тест обработки ошибки при неавторизованном доступе."""
        url = reverse('api:v1:recipes-favorite', kwargs={'pk': recipe.id})
        response = api_client.post(url)
        assert response.status_code == status.HTTP_401_UNAUTHORIZED
