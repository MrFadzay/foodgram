import pytest


@pytest.mark.django_db
def test_get_tags_list(client, create_tag):
    """
    Проверка получения списка тегов.
    API-эндпоинт: /api/tags/
    HTTP-метод: GET
    """
    response = client.get('/api/tags/')
    assert response.status_code == 200
    assert len(response.data) == 1
    assert response.data[0]['name'] == create_tag.name
    assert response.data[0]['slug'] == create_tag.slug
