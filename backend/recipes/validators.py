import re

from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.deconstruct import deconstructible


def validate_hex_color(value):
    """Валидатор для проверки HEX-цвета."""
    if not re.match(r'^#([A-Fa-f0-9]{6}|[A-Fa-f0-9]{3})$', value):
        raise ValidationError(
            'Цвет должен быть в формате HEX (#FFFFFF или #FFF)'
        )


@deconstructible
class CustomEmailValidator(EmailValidator):
    """Расширенный валидатор email."""

    def validate_domain_part(self, domain_part):
        if len(domain_part) > 255:
            raise ValidationError('Домен email слишком длинный')
        return super().validate_domain_part(domain_part)


def validate_image_size(image):
    """Валидатор для проверки размера изображения."""
    limit_mb = 2
    if hasattr(image.file, 'size'):
        file_size = image.file.size
    else:
        file_size = len(image.file.getvalue())

    if file_size > limit_mb * 1024 * 1024:
        raise ValidationError(
            f'Максимальный размер изображения {limit_mb}MB'
        )


def validate_image_extension(value):
    """Валидатор для проверки расширения изображения."""
    valid_extensions = ['.jpg', '.jpeg', '.png']
    ext = value.name.lower()
    if not any(ext.endswith(extension) for extension in valid_extensions):
        raise ValidationError(
            'Поддерживаемые форматы изображений: .jpg, .jpeg, .png'
        )
