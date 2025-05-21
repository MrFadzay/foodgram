from django.conf import settings
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page


class CachedViewSetMixin:
    """Миксин для кэширования результатов viewset."""

    @method_decorator(cache_page(settings.CACHE_TTL))
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @method_decorator(cache_page(settings.CACHE_TTL))
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)
