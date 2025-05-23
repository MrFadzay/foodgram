import pytest
from recipes.models import Recipe, Favorite, ShoppingCart  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore

User = get_user_model()


@pytest.mark.django_db
def test_create_recipe(auth_client, recipe_data):
    """
    Проверка успешного создания нового рецепта авторизованным пользователем.
    API-эндпоинт: /api/recipes/
    HTTP-метод: POST
    """
    response = auth_client.post('/api/recipes/', recipe_data, format='json')
    assert response.status_code == 201
    assert Recipe.objects.filter(name=recipe_data['name']).exists()
    assert response.data['name'] == recipe_data['name']
    assert response.data['cooking_time'] == recipe_data['cooking_time']
    assert len(response.data['tags']) == len(recipe_data['tags'])
    assert len(response.data['ingredients']) == len(recipe_data['ingredients'])


@pytest.mark.django_db
def test_get_recipes_list(client, create_recipe):
    """
    Проверка получения списка рецептов.
    API-эндпоинт: /api/recipes/
    HTTP-метод: GET
    """
    response = client.get('/api/recipes/')
    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['name'] == create_recipe.name


@pytest.mark.django_db
def test_get_recipes_list_filter_favorited(
    auth_client, create_user, create_recipe, create_recipe_2
):
    """
    Проверка фильтрации рецептов по избранному.
    API-эндпоинт: /api/recipes/
    HTTP-метод: GET
    """
    Favorite.objects.create(user=create_user, recipe=create_recipe)
    response = auth_client.get('/api/recipes/?is_favorited=1')
    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['id'] == create_recipe.id

    response = auth_client.get('/api/recipes/?is_favorited=0')
    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['id'] == create_recipe_2.id


@pytest.mark.django_db
def test_get_recipes_list_filter_shopping_cart(
    auth_client, create_user, create_recipe, create_recipe_2
):
    """
    Проверка фильтрации рецептов по списку покупок.
    API-эндпоинт: /api/recipes/
    HTTP-метод: GET
    """
    ShoppingCart.objects.create(user=create_user, recipe=create_recipe)
    response = auth_client.get('/api/recipes/?is_in_shopping_cart=1')
    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['id'] == create_recipe.id

    response = auth_client.get('/api/recipes/?is_in_shopping_cart=0')
    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['id'] == create_recipe_2.id


@pytest.mark.django_db
def test_get_recipes_list_filter_author(
    client, create_user, create_user_2, create_recipe
):
    """
    Проверка фильтрации рецептов по автору.
    API-эндпоинт: /api/recipes/
    HTTP-метод: GET
    """
    response = client.get(f'/api/recipes/?author={create_user.id}')
    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert response.data['results'][0]['author']['id'] == create_user.id

    response = client.get(f'/api/recipes/?author={create_user_2.id}')
    assert response.status_code == 200
    assert len(response.data['results']) == 0


@pytest.mark.django_db
def test_get_recipes_list_filter_tags(client, create_recipe, create_tag):
    """
    Проверка фильтрации рецептов по тегам.
    API-эндпоинт: /api/recipes/
    HTTP-метод: GET
    """
    response = client.get(f'/api/recipes/?tags={create_tag.slug}')
    assert response.status_code == 200
    assert len(response.data['results']) == 1
    assert create_tag.slug in [
        tag['slug'] for tag in response.data['results'][0]['tags']
    ]

    response = client.get('/api/recipes/?tags=nonexistent_tag')
    assert response.status_code == 400
    assert 'tags' in response.data


@pytest.mark.django_db
def test_update_recipe(
    auth_client, create_recipe, create_user, create_tag, create_ingredient
):
    """
    Проверка успешного обновления существующего рецепта его автором.
    API-эндпоинт: /api/recipes/{id}/
    HTTP-метод: PATCH
    """
    updated_data = {
        'name': 'Новый омлет',
        'text': 'Обновленный простой омлет',
        'cooking_time': 15,
        'tags': [create_tag.id],
        'ingredients': [{'id': create_ingredient.id, 'amount': 250}],
        'image': (
            'data:image/png;base64,iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='  # noqa
        )
    }
    response = auth_client.patch(
        f'/api/recipes/{create_recipe.id}/', updated_data, format='json'
    )
    assert response.status_code == 200
    create_recipe.refresh_from_db()
    assert create_recipe.name == updated_data['name']
    assert create_recipe.cooking_time == updated_data['cooking_time']


@pytest.mark.django_db
def test_delete_recipe(auth_client, create_recipe):
    """
    Проверка успешного удаления рецепта его автором.
    API-эндпоинт: /api/recipes/{id}/
    HTTP-метод: DELETE
    """
    response = auth_client.delete(f'/api/recipes/{create_recipe.id}/')
    assert response.status_code == 204
    assert not Recipe.objects.filter(id=create_recipe.id).exists()


@pytest.mark.django_db
def test_add_recipe_to_favorite(auth_client, create_recipe):
    """
    Проверка успешного добавления рецепта в избранное.
    API-эндпоинт: /api/recipes/{id}/favorite/
    HTTP-метод: POST
    """
    response = auth_client.post(f'/api/recipes/{create_recipe.id}/favorite/')
    assert response.status_code == 201
    assert Favorite.objects.filter(recipe=create_recipe).exists()


@pytest.mark.django_db
def test_remove_recipe_from_favorite(auth_client, create_user, create_recipe):
    """
    Проверка успешного удаления рецепта из избранного.
    API-эндпоинт: /api/recipes/{id}/favorite/
    HTTP-метод: DELETE
    """
    Favorite.objects.create(user=create_user, recipe=create_recipe)
    response = auth_client.delete(f'/api/recipes/{create_recipe.id}/favorite/')
    assert response.status_code == 204
    assert not Favorite.objects.filter(recipe=create_recipe).exists()


@pytest.mark.django_db
def test_add_recipe_to_shopping_cart(auth_client, create_recipe):
    """
    Проверка успешного добавления рецепта в список покупок.
    API-эндпоинт: /api/recipes/{id}/shopping_cart/
    HTTP-метод: POST
    """
    response = auth_client.post(
        f'/api/recipes/{create_recipe.id}/shopping_cart/'
    )
    assert response.status_code == 201
    assert ShoppingCart.objects.filter(recipe=create_recipe).exists()


@pytest.mark.django_db
def test_remove_recipe_from_shopping_cart(  # noqa
    auth_client, create_user, create_recipe
):
    """
    Проверка успешного удаления рецепта из списка покупок.
    API-эндпоинт: /api/recipes/{id}/shopping_cart/
    HTTP-метод: DELETE
    """
    ShoppingCart.objects.create(user=create_user, recipe=create_recipe)
    response = auth_client.delete(
        f'/api/recipes/{create_recipe.id}/shopping_cart/'
    )
    assert response.status_code == 204
    assert not ShoppingCart.objects.filter(recipe=create_recipe).exists()


@pytest.mark.django_db
def test_download_shopping_cart(
    auth_client, create_user, create_recipe, create_ingredient
):
    """
    Проверка успешного скачивания списка покупок авторизованным пользователем.
    API-эндпоинт: /api/recipes/download_shopping_cart/
    HTTP-метод: GET
    """
    ShoppingCart.objects.create(user=create_user, recipe=create_recipe)
    response = auth_client.get('/api/recipes/download_shopping_cart/')
    assert response.status_code == 200
    assert response['Content-Type'].startswith('text/plain')
    assert (
        f'{create_ingredient.name} ({create_ingredient.measurement_unit}) - 200'  # noqa
        in response.content.decode('utf-8')
    )
