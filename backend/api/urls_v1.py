from django.urls import include, path
from rest_framework import routers

from api.views import IngredientViewSet, RecipeViewSet, TagViewSet, UserViewSet

app_name = 'v1'

router = routers.DefaultRouter()

router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = router.urls

urlpatterns.extend([
    path('auth/', include('djoser.urls.authtoken')),

    path('users/me/', UserViewSet.as_view({'get': 'me'}), name='users-me'),
    path('users/<int:pk>/subscribe/', UserViewSet.as_view(
        {'post': 'subscribe', 'delete': 'subscribe'}), name='users-subscribe'),
    path(
        'users/subscriptions/',
        UserViewSet.as_view({'get': 'subscriptions'}),
        name='users-subscriptions'
    ),

    path(
        'recipes/<int:pk>/favorite/',
        RecipeViewSet.as_view({'post': 'favorite', 'delete': 'favorite'}),
        name='recipes-favorite'
    ),
    path(
        'recipes/<int:pk>/shopping_cart/',
        RecipeViewSet.as_view(
            {'post': 'shopping_cart', 'delete': 'shopping_cart'}),
        name='recipes-shopping-cart'
    ),
    path(
        'recipes/download_shopping_cart/',
        RecipeViewSet.as_view({'get': 'download_shopping_cart'}),
        name='recipes-download-shopping-cart'
    ),
])
