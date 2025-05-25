import pytest
from rest_framework.test import APIClient  # type: ignore
from django.contrib.auth import get_user_model  # type: ignore
from django.core.files.base import ContentFile
from django.core.files.uploadedfile import SimpleUploadedFile


User = get_user_model()

# Фиктивное изображение 1x1 прозрачный PNG в base64
# Это очень маленькое изображение, которое подходит для тестов.
TEST_IMAGE_BASE64 = (
    'iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNkYAAAAAYAAjCB0C8AAAAASUVORK5CYII='  # noqa
)
# Используем очень маленькое изображение (1x1 прозрачный PNG)
# для имитации загрузки файла.
TEST_IMAGE_BYTES = (
    b'\x89PNG\r\n\x1a\n\x00\x00\x00\rIHDR\x00\x00\x00\x01\x00\x00\x00\x01'
    b'\x08\x06\x00\x00\x00\x1f\x15\xc4\x89\x00\x00\x00\x0cIDATx\xda\xed\xc1'
    b'\x01\x01\x00\x00\x00\xc2\xa0\xf7Om\x00\x00\x00\x00IEND\xaeB`\x82'
)
TEST_IMAGE_CONTENT = ContentFile(TEST_IMAGE_BYTES, name='test_image.png')


@pytest.fixture
def client():
    """Фикстура для тестового клиента DRF."""
    return APIClient()


@pytest.fixture
def user_data():
    """Фикстура для данных тестового пользователя."""
    return {
        'email': 'test@example.com',
        'username': 'testuser',
        'first_name': 'Test',
        'last_name': 'User',
        'password': 'testpassword123',
    }


@pytest.fixture
def create_user(user_data):
    """Фикстура для создания тестового пользователя."""
    user = User.objects.create_user(**user_data)
    return user


@pytest.fixture
def user_data_2():
    """Фикстура для данных второго тестового пользователя."""
    return {
        'email': 'test2@example.com',
        'username': 'testuser2',
        'first_name': 'Test2',
        'last_name': 'User2',
        'password': 'testpassword123',
    }


@pytest.fixture
def create_user_2(user_data_2):
    """Фикстура для создания второго тестового пользователя."""
    user = User.objects.create_user(**user_data_2)
    return user


@pytest.fixture
def auth_client(client, create_user):
    """Фикстура для авторизованного тестового клиента."""
    response = client.post('/api/auth/token/login/', {
        'email': create_user.email,
        'password': 'testpassword123'
    })
    client.credentials(HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')  # noqa
    return client


@pytest.fixture
def auth_client_2(client, create_user_2):
    """Фикстура для второго авторизованного тестового клиента."""
    response = client.post('/api/auth/token/login/', {
        'email': create_user_2.email,
        'password': 'testpassword123'
    })
    client.credentials(HTTP_AUTHORIZATION=f'Token {response.data["auth_token"]}')  # noqa
    return client


@pytest.fixture
def tag_data():
    """Фикстура для данных тестового тега."""
    return {
        'name': 'Завтрак',
        'color': '#E26C2D',
        'slug': 'breakfast'
    }


@pytest.fixture
def create_tag(db, tag_data):
    """Фикстура для создания тестового тега."""
    from recipes.models import Tag  # type: ignore
    tag = Tag.objects.create(**tag_data)
    return tag


@pytest.fixture
def ingredient_data():
    """Фикстура для данных тестового ингредиента."""
    return {
        'name': 'Молоко',
        'measurement_unit': 'мл'
    }


@pytest.fixture
def create_ingredient(db, ingredient_data):
    """Фикстура для создания тестового ингредиента."""
    from recipes.models import Ingredient  # type: ignore
    ingredient = Ingredient.objects.create(**ingredient_data)
    return ingredient


@pytest.fixture
def recipe_data(create_user, create_tag, create_ingredient):
    """Фикстура для данных тестового рецепта."""
    return {
        'name': 'Омлет',
        'text': 'Простой омлет',
        'cooking_time': 10,
        'tags': [create_tag.id],
        'ingredients': [{'id': create_ingredient.id, 'amount': 200}],
        'image': TEST_IMAGE_BASE64  # Используем фиктивное изображение
    }


@pytest.fixture
def create_recipe(db, create_user, create_tag, create_ingredient):
    """Фикстура для создания тестового рецепта."""
    from recipes.models import Recipe, RecipeIngredient  # type: ignore
    recipe = Recipe.objects.create(
        author=create_user,
        name='Омлет',
        text='Простой омлет',
        cooking_time=10,
        image=SimpleUploadedFile(
            'test_image.png',
            TEST_IMAGE_CONTENT.read(),
            content_type='image/png'
        )
    )
    recipe.tags.add(create_tag)
    RecipeIngredient.objects.create(
        recipe=recipe,
        ingredient=create_ingredient,
        amount=200
    )
    return recipe


@pytest.fixture
def recipe_data_2(create_user_2, create_tag, create_ingredient):
    """Фикстура для данных второго тестового рецепта."""
    return {
        'name': 'Яичница',
        'text': 'Простая яичница',
        'cooking_time': 5,
        'tags': [create_tag.id],
        'ingredients': [{'id': create_ingredient.id, 'amount': 100}],
        'image': TEST_IMAGE_BASE64  # Используем фиктивное изображение
    }


@pytest.fixture
def create_recipe_2(db, create_user_2, create_tag, create_ingredient):
    """Фикстура для создания второго тестового рецепта."""
    from recipes.models import Recipe, RecipeIngredient  # type: ignore
    recipe = Recipe.objects.create(
        author=create_user_2,
        name='Яичница',
        text='Простая яичница',
        cooking_time=5,
        image=SimpleUploadedFile(
            'test_image.png',
            TEST_IMAGE_CONTENT.read(),
            content_type='image/png'
        )
    )
    recipe.tags.add(create_tag)
    RecipeIngredient.objects.create(
        recipe=recipe,
        ingredient=create_ingredient,
        amount=100
    )
    return recipe
