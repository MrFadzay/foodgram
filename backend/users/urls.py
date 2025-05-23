from django.urls import include, path
from rest_framework import routers

from api.views import UserViewSet

app_name = 'users'

router = routers.DefaultRouter()
router.register(r'', UserViewSet, basename='users')

urlpatterns = [
    path('', include(router.urls)),
    path(
        'me/avatar/',
        UserViewSet.as_view({'put': 'avatar', 'delete': 'avatar'}),
        name='user-avatar'
    ),
    path(
        'subscriptions/',
        UserViewSet.as_view({'get': 'subscriptions'}),
        name='user-subscriptions'
    ),
]
