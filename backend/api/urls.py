from django.urls import include, path

app_name = 'api'

urlpatterns = [
    path('v1/', include(('api.urls_v1', 'v1'), namespace='v1')),
    # path('v2/', include('api.urls_v2')),  # Для будущих версий API
]
