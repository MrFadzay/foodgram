import pytest
from django.core.exceptions import ValidationError
from django.core.files.uploadedfile import SimpleUploadedFile

from recipes.models import Recipe, Tag
from recipes.validators import (
    validate_hex_color, validate_image_extension, validate_image_size,
)
from users.models import User


@pytest.mark.django_db
class TestValidators:
    def test_hex_color_valid(self):
        """Тест валидных HEX-цветов."""
        valid_colors = ['#FFFFFF', '#000000', '#FF0000', '#FFF', '#000']
        for color in valid_colors:
            validate_hex_color(color)

    def test_hex_color_invalid(self):
        """Тест невалидных HEX-цветов."""
        invalid_colors = ['FFFFFF', '#GGGGGG', '#FFF FFF', '#12345', 'red']
        for color in invalid_colors:
            with pytest.raises(ValidationError):
                validate_hex_color(color)

    def test_image_size_valid(self, tmp_path):
        """Тест валидного размера изображения."""
        small_file = tmp_path / "small.jpg"
        small_file.write_bytes(b"small file content")
        image = SimpleUploadedFile(
            small_file.name,
            small_file.read_bytes(),
            content_type='image/jpeg'
        )
        validate_image_size(image)

    def test_image_size_invalid(self, tmp_path):
        """Тест невалидного размера изображения."""
        # Создаем файл размером больше 2MB
        large_file = tmp_path / "large.jpg"
        large_file.write_bytes(b"x" * (2 * 1024 * 1024 + 1))
        image = SimpleUploadedFile(
            large_file.name,
            large_file.read_bytes(),
            content_type='image/jpeg'
        )
        with pytest.raises(ValidationError):
            validate_image_size(image)

    def test_image_extension_valid(self, tmp_path):
        """Тест валидных расширений изображений."""
        valid_extensions = ['.jpg', '.jpeg', '.png']
        for ext in valid_extensions:
            file = tmp_path / f"test{ext}"
            file.write_bytes(b"test content")
            image = SimpleUploadedFile(
                file.name,
                file.read_bytes(),
                content_type='image/jpeg'
            )
            validate_image_extension(image)

    def test_image_extension_invalid(self, tmp_path):
        """Тест невалидных расширений изображений."""
        invalid_extensions = ['.gif', '.bmp', '.tiff', '.pdf']
        for ext in invalid_extensions:
            file = tmp_path / f"test{ext}"
            file.write_bytes(b"test content")
            image = SimpleUploadedFile(
                file.name,
                file.read_bytes(),
                content_type='image/gif'
            )
            with pytest.raises(ValidationError):
                validate_image_extension(image)


@pytest.mark.django_db
class TestModelValidation:
    def test_tag_color_validation(self):
        """Тест валидации цвета тега."""
        tag = Tag(name='Test', slug='test', color='invalid-color')
        with pytest.raises(ValidationError):
            tag.full_clean()

        tag.color = '#FFFFFF'
        tag.full_clean()

    def test_recipe_image_validation(self, tmp_path):
        """Тест валидации изображения рецепта."""
        user = User.objects.create(
            username='testuser',
            email='test@example.com',
            password='testpass'
        )

        # Тест невалидного размера
        large_file = tmp_path / "large.jpg"
        large_file.write_bytes(b"x" * (2 * 1024 * 1024 + 1))
        image = SimpleUploadedFile(
            large_file.name,
            large_file.read_bytes(),
            content_type='image/jpeg'
        )

        recipe = Recipe(
            author=user,
            name='Test Recipe',
            text='Test description',
            cooking_time=30,
            image=image
        )

        with pytest.raises(ValidationError):
            recipe.full_clean()

        # Тест невалидного расширения
        invalid_file = tmp_path / "test.gif"
        invalid_file.write_bytes(b"test content")
        image = SimpleUploadedFile(
            invalid_file.name,
            invalid_file.read_bytes(),
            content_type='image/gif'
        )

        recipe.image = image
        with pytest.raises(ValidationError):
            recipe.full_clean()
