from functools import wraps

from django.core.cache import cache
from rest_framework import status
from rest_framework.response import Response


def rate_limit(requests=60, interval=60, key_prefix='default'):
    """
    Декоратор для ограничения количества запросов к API.

    Args:
        requests (int): Максимальное количество запросов
        interval (int): Интервал времени в секундах
        key_prefix (str): Префикс для ключа кэша
    """
    def decorator(view_func):
        @wraps(view_func)
        def _wrapped_view(view_instance, request, *args, **kwargs):
            # Формируем ключ для кэша
            key = f"rate_limit:{key_prefix}:{request.META.get('REMOTE_ADDR')}"

            # Получаем текущее количество запросов
            requests_count = cache.get(key, 0)

            if requests_count >= requests:
                return Response(
                    {"detail": "Слишком много запросов. Попробуйте позже."},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # Увеличиваем счетчик запросов
            cache.set(key, requests_count + 1, interval)

            return view_func(view_instance, request, *args, **kwargs)
        return _wrapped_view
    return decorator


def method_rate_limit(requests=None, interval=None):
    """
    Декоратор для ограничения запросов к конкретным методам API.

    Args:
        requests (dict): Словарь с лимитами для каждого метода
        interval (dict): Словарь с интервалами для каждого метода
    """
    if requests is None:
        requests = {
            'GET': 100,
            'POST': 50,
            'PUT': 30,
            'PATCH': 30,
            'DELETE': 20
        }

    if interval is None:
        interval = {
            'GET': 60,
            'POST': 60,
            'PUT': 60,
            'PATCH': 60,
            'DELETE': 60
        }

    def decorator(view_class):
        original_dispatch = view_class.dispatch

        def rate_limited_dispatch(self, request, *args, **kwargs):
            method = request.method
            if method not in requests:
                return original_dispatch(self, request, *args, **kwargs)

            key_prefix = f"{self.__class__.__name__}_{method}"
            return rate_limit(
                requests=requests[method],
                interval=interval[method],
                key_prefix=key_prefix
            )(original_dispatch)(self, request, *args, **kwargs)

        view_class.dispatch = rate_limited_dispatch
        return view_class

    return decorator
