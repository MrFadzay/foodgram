from django.core.validators import MinValueValidator
from django.db import transaction
from djoser.serializers import (
    UserCreateSerializer as DjoserUserCreateSerializer,
)
from drf_extra_fields.fields import Base64ImageField
from rest_framework import serializers

from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag,
)
from users.models import Follow, User

from .constants import MIN_AMOUNT_AND_COOKING_TIME


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = '__all__'


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = '__all__'


class RecipeIngredientReadSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeIngredientWriteSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all(),
        source='ingredient'
    )
    amount = serializers.IntegerField(
        validators=[MinValueValidator(MIN_AMOUNT_AND_COOKING_TIME)]
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class UserSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    avatar = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'avatar',
        )

    def get_is_subscribed(self, obj):
        request = self.context.get('request')
        return bool(
            request
            and request.user.is_authenticated
            and obj.following.filter(user=request.user).exists()
        )

    def get_avatar(self, obj):
        if obj.avatar and obj.avatar.name:
            return obj.avatar.url
        return None


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientReadSerializer(
        source='recipe_ingredients',
        many=True,
        read_only=True
    )
    image = serializers.ImageField(read_only=True, use_url=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'image',
            'text',
            'cooking_time',
            'is_favorited',
            'is_in_shopping_cart',
        )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        return bool(
            request
            and request.user.is_authenticated
            and obj.favorites.filter(user=request.user).exists()
        )

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        return bool(
            request
            and request.user.is_authenticated
            and obj.shopping_cart.filter(user=request.user).exists()
        )


class RecipeCreateUpdateSerializer(RecipeSerializer):
    ingredients = RecipeIngredientWriteSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all(),
    )
    image = Base64ImageField(required=False)
    cooking_time = serializers.IntegerField(
        validators=[MinValueValidator(MIN_AMOUNT_AND_COOKING_TIME)]
    )

    class Meta:
        model = Recipe
        fields = (
            'ingredients',
            'tags',
            'image',
            'name',
            'text',
            'cooking_time',
        )

    def validate(self, data):

        ingredients = data.get('ingredients')
        if not ingredients:
            raise serializers.ValidationError(
                'Добавьте хотя бы один ингредиент.'
            )
        ingredient_ids = [
            ingredient['ingredient'].id for ingredient in ingredients
        ]
        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError(
                'Ингредиенты не должны повторяться.'
            )

        tags = data.get('tags')
        if not tags:
            raise serializers.ValidationError('Выберите хотя бы один тег.')
        if len(tags) != len(set(tags)):
            raise serializers.ValidationError('Теги не должны повторяться.')

        if self.context.get('request').method == 'POST':
            if 'image' not in data:
                raise serializers.ValidationError(
                    'Добавьте изображение.',
                )
        return data

    def to_representation(self, instance):
        return RecipeSerializer(instance, context=self.context).data

    def _set_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            [
                RecipeIngredient(
                    recipe=recipe,
                    ingredient=ingredient_data['ingredient'],
                    amount=ingredient_data['amount']
                )
                for ingredient_data in ingredients
            ]
        )

    @transaction.atomic
    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        author = self.context.get('request').user
        recipe = Recipe.objects.create(author=author, **validated_data)
        recipe.tags.set(tags)
        self._set_ingredients(recipe, ingredients)
        return recipe

    @transaction.atomic
    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        if 'image' in validated_data and (
            validated_data['image'] is None or validated_data['image'] == ''
        ):
            validated_data.pop('image')

        instance.tags.clear()
        instance.tags.set(tags)
        instance.ingredients.clear()
        self._set_ingredients(instance, ingredients)

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class RecipeShortSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(UserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',
            'recipes',
            'recipes_count',
            'avatar',
        )

    def get_recipes(self, obj):
        request = self.context.get('request')
        if not request:
            return []
        limit = request.GET.get('recipes_limit')
        recipes = obj.recipes.all().order_by('id')
        if limit:
            try:
                recipes = recipes[:int(limit)]
            except ValueError:
                pass
        serializer = RecipeShortSerializer(
            recipes, many=True, context={'request': request}
        )
        return serializer.data

    def get_recipes_count(self, obj):
        return obj.recipes.count()


class FollowCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Follow
        fields = ('user', 'author')

    def validate(self, data):
        request = self.context.get('request')
        if (
            request is None
            or not request.user
            or not request.user.is_authenticated
        ):
            raise serializers.ValidationError(
                'Требуется аутентификация для подписки.'
            )
        user = request.user
        author = data['author']

        if user == author:
            raise serializers.ValidationError(
                'Нельзя подписаться на самого себя.'
            )
        if Follow.objects.filter(user=user, author=author).exists():
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя.'
            )
        return data


class FavoriteCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if (
            request is None
            or not request.user
            or not request.user.is_authenticated
        ):
            raise serializers.ValidationError(
                'Требуется аутентификация для добавления в избранное.'
            )
        user = request.user
        recipe = data['recipe']

        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в избранное.'
            )
        return data


class ShoppingCartCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        request = self.context.get('request')
        if (
            request is None
            or not request.user
            or not request.user.is_authenticated
        ):
            raise serializers.ValidationError(
                'Требуется аутентификация для добавления в список покупок.'
            )
        user = request.user
        recipe = data['recipe']

        if ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            raise serializers.ValidationError(
                'Рецепт уже добавлен в список покупок.'
            )
        return data


class UserCreateSerializer(DjoserUserCreateSerializer):
    class Meta(DjoserUserCreateSerializer.Meta):
        fields = (
            'email',
            'username',
            'first_name',
            'last_name',
            'password',
        )


class UserResponseOnCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
        )


class SetAvatarSerializer(serializers.ModelSerializer):
    avatar = Base64ImageField(required=True)

    class Meta:
        model = User
        fields = ('avatar',)
