import pytest
from django.contrib.auth import get_user_model  # type: ignore
from users.models import Follow  # type: ignore

User = get_user_model()


@pytest.mark.django_db
def test_user_registration(client, user_data):
    """
    Проверка успешной регистрации нового пользователя.
    API-эндпоинт: /api/users/
    HTTP-метод: POST
    """
    response = client.post('/api/users/', user_data)
    assert response.status_code == 201
    assert User.objects.filter(email=user_data['email']).exists()
    assert 'email' in response.data
    assert 'username' in response.data


@pytest.mark.django_db
def test_get_auth_token(client, create_user):
    """
    Проверка успешного получения токена авторизации для существующего пользователя.  # noqa
    API-эндпоинт: /api/auth/token/login/
    HTTP-метод: POST
    """
    response = client.post('/api/auth/token/login/', {
        'email': create_user.email,
        'password': 'testpassword123'
    })
    assert response.status_code == 200
    assert 'auth_token' in response.data


@pytest.mark.django_db
def test_logout(auth_client):
    """
    Проверка успешного удаления токена авторизации (выход из системы).
    API-эндпоинт: /api/auth/token/logout/
    HTTP-метод: POST
    """
    response = auth_client.post('/api/auth/token/logout/')
    assert response.status_code == 204


@pytest.mark.django_db
def test_set_password(auth_client, create_user):
    """
    Проверка успешного изменения пароля текущего пользователя.
    API-эндпоинт: /api/users/set_password/
    HTTP-метод: POST
    """
    old_password = 'testpassword123'
    new_password = 'new_testpassword123'
    response = auth_client.post('/api/users/set_password/', {
        'new_password': new_password,
        'current_password': old_password
    })
    assert response.status_code == 204

    # Проверяем, что можно войти с новым паролем
    client = auth_client
    client.credentials()  # Сбрасываем старый токен
    response = client.post('/api/auth/token/login/', {
        'email': create_user.email,
        'password': new_password
    })
    assert response.status_code == 200
    assert 'auth_token' in response.data


@pytest.mark.django_db
def test_get_current_user_info(auth_client, create_user):
    """
    Проверка получения информации о текущем авторизованном пользователе.
    API-эндпоинт: /api/users/me/
    HTTP-метод: GET
    """
    response = auth_client.get('/api/users/me/')
    assert response.status_code == 200
    assert response.data['email'] == create_user.email
    assert response.data['username'] == create_user.username


@pytest.mark.django_db
def test_subscribe_to_user(auth_client, create_user, create_user_2):
    """
    Проверка успешной подписки на другого пользователя.
    API-эндпоинт: /api/users/{id}/subscribe/
    HTTP-метод: POST
    """
    response = auth_client.post(f'/api/users/{create_user_2.id}/subscribe/')
    assert response.status_code == 201
    assert response.data['id'] == create_user_2.id
    assert Follow.objects.filter(
        user=create_user, author=create_user_2
    ).exists()


@pytest.mark.django_db
def test_unsubscribe_from_user(auth_client, create_user, create_user_2):
    """
    Проверка успешной отписки от пользователя.
    API-эндпоинт: /api/users/{id}/subscribe/
    HTTP-метод: DELETE
    """
    # Сначала подписываемся
    auth_client.post(f'/api/users/{create_user_2.id}/subscribe/')
    assert Follow.objects.filter(
        user=create_user, author=create_user_2
    ).exists()

    # Затем отписываемся
    response = auth_client.delete(f'/api/users/{create_user_2.id}/subscribe/')
    assert response.status_code == 204
    assert not Follow.objects.filter(
        user=create_user, author=create_user_2
    ).exists()
