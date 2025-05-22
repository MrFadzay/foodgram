from django.urls import include, path

app_name = 'api'

urlpatterns = [
    path('', include(('api.urls_v1', 'v1'), namespace='v1')),
]
