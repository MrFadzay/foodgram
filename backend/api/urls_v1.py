from django.urls import include, path

app_name = 'v1'

urlpatterns = [
    path('users/', include(('users.urls', 'users'), namespace='users')),
    path('', include(('recipes.urls', 'recipes'), namespace='recipes')),
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
]
