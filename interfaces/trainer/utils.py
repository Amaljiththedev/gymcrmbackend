from django.core.cache import cache

def get_cached_data(key):
    return cache.get(key)

def set_cached_data(key, data, timeout=60*5):  # cache timeout of 5 minutes
    cache.set(key, data, timeout)
