from django.urls import include, path
from djoser import views as djoser_views

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
    path('auth/', include('djoser.urls.authtoken')),
]
