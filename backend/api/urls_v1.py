from django.urls import include, path
from djoser import views as djoser_views

from api.views import RecipeViewSet

app_name = 'v1'

urlpatterns = [
    path(
        'users/set_password/',
        djoser_views.UserViewSet.as_view({'post': 'set_password'}),
        name='set_password'
    ),
    path(
        'users/reset_password/',
        djoser_views.UserViewSet.as_view({'post': 'reset_password'}),
        name='reset_password'
    ),
    path(
        'users/reset_password_confirm/',
        djoser_views.UserViewSet.as_view({'post': 'reset_password_confirm'}),
        name='password_reset_confirm'
    ),
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('', include(('recipes.urls', 'recipes'), namespace='recipes')),
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
    path('auth/', include('djoser.urls.authtoken')),
]
