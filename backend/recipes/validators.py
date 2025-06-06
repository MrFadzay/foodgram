from django.core.exceptions import ValidationError


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
