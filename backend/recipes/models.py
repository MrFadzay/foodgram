from django.core.validators import MinValueValidator
from django.db import models

from users.models import User

from .constants import (
    MAX_LENGTH_INGREDIENT_MEASUREMENT_UNIT, MAX_LENGTH_INGREDIENT_NAME,
    MAX_LENGTH_RECIPE_NAME, MAX_LENGTH_TAG_NAME, MAX_LENGTH_TAG_SLUG,
    MESSAGE_MIN_AMOUNT, MESSAGE_MIN_COOKING_TIME, MIN_AMOUNT, MIN_COOKING_TIME,
)
from .validators import validate_image_extension, validate_image_size


class Tag(models.Model):
    """Модель тегов."""
    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_TAG_NAME,
        unique=True,
    )
    slug = models.SlugField(
        'Уникальный слаг',
        max_length=MAX_LENGTH_TAG_SLUG,
        unique=True,
    )

    class Meta:
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'
        ordering = ['name']

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Модель ингредиентов."""
    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_INGREDIENT_NAME,
    )
    measurement_unit = models.CharField(
        'Единица измерения',
        max_length=MAX_LENGTH_INGREDIENT_MEASUREMENT_UNIT,
    )

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ['name']
        constraints = [
            models.UniqueConstraint(
                fields=['name', 'measurement_unit'],
                name='unique_ingredient'
            )
        ]

    def __str__(self):
        return f'{self.name}, {self.measurement_unit}'


class Recipe(models.Model):
    """Модель рецептов."""
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор',
    )
    name = models.CharField(
        'Название',
        max_length=MAX_LENGTH_RECIPE_NAME,
    )
    image = models.ImageField(
        'Картинка',
        upload_to='recipes/',
        validators=[validate_image_size, validate_image_extension],
        blank=True,
        null=True,
    )
    text = models.TextField(
        'Описание',
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='RecipeIngredient',
        verbose_name='Ингредиенты',
    )
    tags = models.ManyToManyField(
        Tag,
        verbose_name='Теги',
    )
    cooking_time = models.PositiveSmallIntegerField(
        'Время приготовления (в минутах)',
        validators=[
            MinValueValidator(
                MIN_COOKING_TIME,
                message=MESSAGE_MIN_COOKING_TIME
            )
        ]
    )
    pub_date = models.DateTimeField(
        'Дата публикации',
        auto_now_add=True,
        db_index=True,
    )

    class Meta:
        default_related_name = 'recipes'
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ['-pub_date']

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    """Модель связи рецепта и ингредиента."""
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
        related_name='recipe_ingredients',
    )
    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент',
        related_name='recipe_ingredients',
    )
    amount = models.PositiveSmallIntegerField(
        'Количество',
        validators=[
            MinValueValidator(MIN_AMOUNT, message=MESSAGE_MIN_AMOUNT)
        ]
    )

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'
        constraints = [
            models.UniqueConstraint(
                fields=['recipe', 'ingredient'],
                name='unique_recipe_ingredient'
            )
        ]

    def __str__(self):
        return (
            f'{self.ingredient.name} ({self.amount} '
            f'{self.ingredient.measurement_unit})'
        )


class BaseUserRecipeRelation(models.Model):
    """Абстрактная модель для связи пользователя и рецепта."""
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Пользователь',
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт',
    )

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='%(app_label)s_%(class)s_unique_relation'
            )
        ]

    def __str__(self):
        return f'{self.user.username} -> {self.recipe.name}'


class Favorite(BaseUserRecipeRelation):
    """Модель избранных рецептов."""

    class Meta(BaseUserRecipeRelation.Meta):
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        default_related_name = 'favorites'


class ShoppingCart(BaseUserRecipeRelation):
    """Модель списка покупок."""

    class Meta(BaseUserRecipeRelation.Meta):
        verbose_name = 'Список покупок'
        verbose_name_plural = 'Списки покупок'
        default_related_name = 'shopping_cart'
