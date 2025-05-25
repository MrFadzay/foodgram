from django.db.models import Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from api.decorators import method_rate_limit
from recipes.models import (
    Favorite, Ingredient, Recipe, RecipeIngredient, ShoppingCart, Tag,
)
from users.models import Follow, User

from .filters import RecipeFilter
from .mixins import CachedViewSetMixin
from .permissions import IsAuthorOrReadOnly
from .serializers import (
    CustomUserCreateSerializer, CustomUserResponseOnCreateSerializer,
    FollowSerializer, IngredientSerializer, RecipeCreateUpdateSerializer,
    RecipeSerializer, RecipeShortSerializer, SetAvatarSerializer,
    TagSerializer, UserSerializer,
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

    def get_queryset(self):
        queryset = super().get_queryset()
        name = self.request.query_params.get('name')
        if name:
            return queryset.filter(name__istartswith=name)
        return queryset


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
            return CustomUserCreateSerializer
        elif self.action == 'subscribe':
            return FollowSerializer
        return UserSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response_serializer = CustomUserResponseOnCreateSerializer(
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

    pagination_class = PageNumberPagination

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def me(self, request):
        if not request.user.is_authenticated:
            return Response(status=status.HTTP_401_UNAUTHORIZED)
        serializer = self.get_serializer(request.user)
        return Response(serializer.data)

    @action(
        detail=False,
        methods=['put', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def avatar(self, request):
        if request.method == 'PUT':
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
        if request.method == 'DELETE':
            request.user.avatar = None
            request.user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def subscribe(self, request, pk=None):
        user = request.user
        author = get_object_or_404(User, pk=pk)

        if request.method == 'POST':
            if user == author:
                return Response(
                    {'errors': 'Нельзя подписаться на самого себя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            if Follow.objects.filter(user=user, author=author).exists():
                return Response(
                    {'errors': 'Вы уже подписаны на этого пользователя'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            follow = Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(
                author, context={'request': request}
            )
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            follow = Follow.objects.filter(user=user, author=author)
            if follow.exists():
                follow.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'detail': 'Вы не подписаны на этого пользователя'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=False,
        methods=['get'],
        permission_classes=[IsAuthenticated]
    )
    def subscriptions(self, request):
        user = request.user
        authors = User.objects.filter(following__user=user).prefetch_related(
            'recipes'
        )
        pages = self.paginate_queryset(authors)
        serializer = FollowSerializer(
            pages,
            many=True,
            context={'request': request}
        )
        return self.get_paginated_response(serializer.data)


@method_rate_limit()
class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.select_related(
        'author'
    ).prefetch_related(
        'tags',
        'ingredients',
        'recipe_ingredients',
        'favorites',
        'shopping_cart'
    )
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter
    pagination_class = PageNumberPagination

    def get_serializer_class(self):
        if self.action in ('create', 'partial_update'):
            return RecipeCreateUpdateSerializer
        return RecipeSerializer

    def get_serializer_context(self):
        return {'request': self.request}

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def favorite(self, request, pk=None):
        return self.add_to_list(request, pk, Favorite)

    @action(
        detail=True,
        methods=['post', 'delete'],
        permission_classes=[IsAuthenticated]
    )
    def shopping_cart(self, request, pk=None):
        return self.add_to_list(request, pk, ShoppingCart)

    def add_to_list(self, request, pk, model):
        user = request.user
        recipe = get_object_or_404(Recipe, pk=pk)

        if not user.is_authenticated:
            return Response(
                {'errors': 'Требуется аутентификация'},
                status=status.HTTP_401_UNAUTHORIZED
            )

        if request.method == 'POST':
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': 'Рецепт уже добавлен'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=user, recipe=recipe)
            serializer = RecipeShortSerializer(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            obj = model.objects.filter(user=user, recipe=recipe)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': 'Рецепт не найден в списке'},
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
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        if not ingredients:
            return Response(
                {'errors': 'Нет ингредиентов для списка покупок'},
                status=status.HTTP_400_BAD_REQUEST
            )

        shopping_list = []
        for ingredient in ingredients:
            shopping_list.append(
                f'{ingredient["ingredient__name"]} '
                f'({ingredient["ingredient__measurement_unit"]}) - '
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
