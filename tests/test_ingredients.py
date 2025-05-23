import pytest


@pytest.mark.django_db
def test_get_ingredients_list(client, create_ingredient):
    """
    Проверка получения списка ингредиентов.
    API-эндпоинт: /api/ingredients/
    HTTP-метод: GET
    """
    response = client.get('/api/ingredients/')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == create_ingredient.name
    assert response.data[0]['measurement_unit'] == (
        create_ingredient.measurement_unit
    )


@pytest.mark.django_db
def test_get_ingredients_list_with_search(client, create_ingredient):
    """
    Проверка получения списка ингредиентов с фильтрацией по имени.
    API-эндпоинт: /api/ingredients/
    HTTP-метод: GET
    """
    response = client.get('/api/ingredients/?name=Молоко')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == create_ingredient.name

    response = client.get('/api/ingredients/?name=Вода')
    assert response.status_code == 200
    assert len(response.data) == 0
