from django.urls import include, path

app_name = 'v1'

urlpatterns = [
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('users/', include('djoser.urls')),
    path('', include(('recipes.urls', 'recipes'), namespace='recipes')),
    path('auth/', include('djoser.urls.authtoken')),
]
