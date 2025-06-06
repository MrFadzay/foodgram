from django.contrib.auth.models import AbstractUser
from django.db import models

from users.constants import (
    MAX_LENGTH_EMAIL, MAX_LENGTH_FIRST_NAME, MAX_LENGTH_LAST_NAME,
)
from users.validators import CustomEmailValidator


class User(AbstractUser):
    """
    Модель пользователя с дополнительными полями.
    """
    email = models.EmailField(
        'Email',
        max_length=MAX_LENGTH_EMAIL,
        unique=True,
        validators=[CustomEmailValidator()],
    )
    first_name = models.CharField(
        'Имя',
        max_length=MAX_LENGTH_FIRST_NAME,
    )
    last_name = models.CharField(
        'Фамилия',
        max_length=MAX_LENGTH_LAST_NAME,
    )
    avatar = models.ImageField(
        'Аватар',
        upload_to='users/',
        blank=True,
        null=True,
        default=''
    )

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    class Meta:
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'
        ordering = ['username']

    def __str__(self):
        return self.username


class Follow(models.Model):
    """
    Модель подписки на авторов.
    """
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Подписчик'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'],
                name='unique_follow'
            )
        ]

    def __str__(self):
        return f'{self.user.username} -> {self.author.username}'

    def clean(self):
        from django.core.exceptions import ValidationError
        if self.user == self.author:
            raise ValidationError('Вы не можете подписаться на самого себя.')
