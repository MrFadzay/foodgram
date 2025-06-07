from django.db.models import (
    Sum, Count, Exists, OuterRef, Value, BooleanField, F
)
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .pagination import CustomPageNumberPagination

from api.decorators import method_rate_limit
from recipes.models import (
    Favorite, Ingredient, RecipeIngredient, ShoppingCart, Tag,
)
from recipes.models import Recipe
from users.models import Follow, User

from .filters import IngredientFilter, RecipeFilter
from .mixins import CachedViewSetMixin
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    UserCreateSerializer, UserResponseOnCreateSerializer,
    FollowSerializer, FollowCreateSerializer, FavoriteCreateSerializer,
    ShoppingCartCreateSerializer, IngredientSerializer,
    RecipeCreateUpdateSerializer, RecipeSerializer, RecipeShortSerializer,
    SetAvatarSerializer, TagSerializer, UserSerializer,
)


@method_rate_limit(requests={'GET': 200})
class TagViewSet(CachedViewSetMixin,
                 mixins.ListModelMixin,
                 mixins.RetrieveModelMixin,
                 viewsets.GenericViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = (AllowAny,)
    pagination_class = None


@method_rate_limit(requests={'GET': 200})
class IngredientViewSet(CachedViewSetMixin, viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    pagination_class = None
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter


@method_rate_limit()
class UserViewSet(mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  mixins.CreateModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all().prefetch_related(
        'follower',
        'following'
    )

    def get_serializer_class(self):
        if self.action == 'create':
            return UserCreateSerializer
        elif self.action == 'subscribe':
            return FollowCreateSerializer
        elif self.action == 'subscriptions':
            return FollowSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response_serializer = UserResponseOnCreateSerializer(
            serializer.instance
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED,
            headers=headers
        )

    def get_permissions(self):
        if self.action in ('list', 'retrieve', 'create'):
            return (AllowAny(),)
        return (IsAuthenticated(),)

    pagination_class = CustomPageNumberPagination

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='me'
    )
    def me(self, request):
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request):
        if not request.data:
            return Response(
                {'errors': 'Тело запроса не может быть пустым.'},
                status=status.HTTP_400_BAD_REQUEST
            )
        serializer = SetAvatarSerializer(
            request.user, data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response(serializer.data, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        if request.user.avatar:
            request.user.avatar.delete(save=False)
        request.user.avatar = None
        request.user.save()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated],
        url_path='subscribe'
    )
    def subscribe(self, request, pk=None):
        author = get_object_or_404(User, pk=pk)
        serializer = self.get_serializer(
            data={'user': request.user.id, 'author': author.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = FollowSerializer(
            author, context={'request': request}
        )
        return Response(
            response_serializer.data,
            status=status.HTTP_201_CREATED
        )

    @subscribe.mapping.delete
    def delete_subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)

        deleted_count, _ = Follow.objects.filter(
            user=user, author=author).delete()
        if deleted_count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'detail': 'Вы не подписаны на этого пользователя'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated],
        url_path='subscriptions'
    )
    def subscriptions(self, request):
        user = request.user
        authors = User.objects.filter(
            following__user=user
        ).annotate(
            recipes_count=Count('recipes')
        ).prefetch_related('recipes')
        pages = self.paginate_queryset(authors)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


@method_rate_limit()
class RecipeViewSet(viewsets.ModelViewSet):
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = CustomPageNumberPagination

    def get_queryset(self):
        user = self.request.user
        queryset = Recipe.objects.select_related(
            'author'
        ).prefetch_related(
            'tags',
            'ingredients',
            'recipe_ingredients',
            'favorites',
            'shopping_cart'
        )
        if user.is_authenticated:
            queryset = queryset.annotate(
                is_favorited=Exists(
                    Favorite.objects.filter(
                        user=user,
                        recipe=OuterRef('pk')
                    )
                ),
                is_in_shopping_cart=Exists(
                    ShoppingCart.objects.filter(
                        user=user,
                        recipe=OuterRef('pk')
                    )
                )
            )
        else:
            queryset = queryset.annotate(
                is_favorited=Value(False, output_field=BooleanField()),
                is_in_shopping_cart=Value(False, output_field=BooleanField())
            )
        return queryset

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer
        if self.action == 'favorite':
            return FavoriteCreateSerializer
        if self.action == 'shopping_cart':
            return ShoppingCartCreateSerializer
        return RecipeSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        serializer.save()

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = self.get_serializer(
            data={'user': request.user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = RecipeShortSerializer(recipe)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED
        )

    @favorite.mapping.delete
    def delete_favorite(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        deleted_count, _ = Favorite.objects.filter(
            user=user, recipe=recipe).delete()
        if deleted_count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепт не найден в избранном'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['post'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        recipe = get_object_or_404(Recipe, pk=pk)
        serializer = self.get_serializer(
            data={'user': request.user.id, 'recipe': recipe.id},
            context={'request': request}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        response_serializer = RecipeShortSerializer(recipe)
        return Response(
            response_serializer.data, status=status.HTTP_201_CREATED
        )

    @shopping_cart.mapping.delete
    def delete_shopping_cart(self, request, pk=None):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        deleted_count, _ = ShoppingCart.objects.filter(
            user=user, recipe=recipe).delete()
        if deleted_count > 0:
            return Response(status=status.HTTP_204_NO_CONTENT)
        return Response(
            {'errors': 'Рецепт не найден в списке покупок'},
            status=status.HTTP_400_BAD_REQUEST
        )

    @action(
        detail=True,
        methods=['get'],
        permission_classes=[AllowAny]
    )
    def get_link(self, request, pk=None):
        recipe: Recipe = get_object_or_404(Recipe, pk=pk)
        short_link = request.build_absolute_uri(f'/recipes/{recipe.id}/')
        return Response({'short-link': short_link}, status=status.HTTP_200_OK)

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def download_shopping_cart(self, request):
        user = request.user
        if not user.shopping_cart.exists():
            return Response(
                {'errors': 'Список покупок пуст'},
                status=status.HTTP_400_BAD_REQUEST
            )

        ingredients = RecipeIngredient.objects.select_related(
            'ingredient'
        ).filter(
            recipe__shopping_cart__user=user
        ).values(
            name=F('ingredient__name'),
            measurement_unit=F('ingredient__measurement_unit')
        ).annotate(amount=Sum('amount'))

        if not ingredients:
            return Response(
                {'errors': 'Нет ингредиентов для списка покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )

        shopping_list = []
        for ingredient in ingredients:
            shopping_list.append(
                f'{ingredient["name"]} '
                f'({ingredient["measurement_unit"]}) - '
                f'{ingredient["amount"]}'
            )
        shopping_list = '\n'.join(shopping_list)

        response = HttpResponse(
            shopping_list,
            content_type='text/plain; charset=utf-8'
        )
        response['Content-Disposition'] = (
            'attachment; filename="shopping_list.txt"'
        )
        return response
