from django.core.exceptions import ValidationError
from django.core.validators import EmailValidator
from django.utils.deconstruct import deconstructible


@deconstructible
class CustomEmailValidator(EmailValidator):
    """
    Расширенный валидатор email.
    """

    def validate_domain_part(self, domain_part):
        if len(domain_part) > 255:
            raise ValidationError('Домен email слишком длинный')
        return super().validate_domain_part(domain_part)
