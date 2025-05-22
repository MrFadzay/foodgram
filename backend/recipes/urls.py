from django.urls import path, include
from rest_framework import routers

from api.views import TagViewSet, IngredientViewSet, RecipeViewSet

app_name = 'recipes'

router = routers.DefaultRouter()
router.register(r'tags', TagViewSet, basename='tags')
router.register(r'ingredients', IngredientViewSet, basename='ingredients')
router.register(r'recipes', RecipeViewSet, basename='recipes')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'recipes/<int:pk>/favorite/',
        RecipeViewSet.as_view({'post': 'favorite', 'delete': 'favorite'}),
        name='recipes-favorite'
    ),
    path(
        'recipes/<int:pk>/shopping_cart/',
        RecipeViewSet.as_view(
            {'post': 'shopping_cart', 'delete': 'shopping_cart'}
        ),
        name='recipes-shopping-cart'
    ),
    path(
        'recipes/download_shopping_cart/',
        RecipeViewSet.as_view({'get': 'download_shopping_cart'}),
        name='recipes-download-shopping-cart'
    ),
    path(
        'recipes/<int:pk>/get-link/',
        RecipeViewSet.as_view({'get': 'get_link'}),
        name='recipes-get-link'
    ),
]