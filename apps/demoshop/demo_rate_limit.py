"""Rate limiting middleware для demo auth endpoints.

Захист від brute-force на КП-лінк і token exchange.
"""
from django.core.cache import cache
from django.http import HttpResponse


def _get_client_ip(request):
    """Отримати IP клієнта з урахуванням proxy."""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        return x_forwarded_for.split(',')[0].strip()
    return request.META.get('REMOTE_ADDR', '')


class DemoAuthRateLimitMiddleware:
    """Rate limiting для /demo/<slug>/open/* і /demo-admin/<slug>/exchange/.
    
    Ліміт: 10 спроб на IP+demo за 10 хвилин.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.rate_limit = 10
        self.window_seconds = 600  # 10 хвилин
    
    def __call__(self, request):
        # Перевіряємо тільки demo auth endpoints
        path = request.path
        if not (path.startswith('/demo/') or path.startswith('/demo-admin/')):
            return self.get_response(request)
        
        # Витягуємо slug з URL
        parts = path.strip('/').split('/')
        if len(parts) < 2:
            return self.get_response(request)
        
        demo_slug = parts[1]
        ip = _get_client_ip(request)
        
        # Перевіряємо тільки /open/ і /exchange/
        is_protected = (
            '/open/' in path or 
            '/exchange/' in path
        )
        
        if not is_protected:
            return self.get_response(request)
        
        # Cache key: rate_limit:demo:<slug>:<ip>
        cache_key = f'rate_limit:demo:{demo_slug}:{ip}'
        
        # Отримуємо поточну кількість спроб
        attempts = cache.get(cache_key, 0)
        
        if attempts >= self.rate_limit:
            response = HttpResponse(
                'Too many requests. Please try again later.',
                status=429
            )
            response['Retry-After'] = str(self.window_seconds)
            return response
        
        # Інкрементуємо лічильник
        cache.set(cache_key, attempts + 1, self.window_seconds)
        
        return self.get_response(request)
