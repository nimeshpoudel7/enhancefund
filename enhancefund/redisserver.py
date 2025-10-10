from django.http import JsonResponse
import redis


r = redis.Redis(
  host='redis-12912.crce174.ca-central-1-1.ec2.redns.redis-cloud.com',
  port=12912,
  password='ZaO5aijLXv3P42drftikEcj9WtSsvYqQ')
def set_cache_value(key, value, timeout=60*15):
    """
    Set a value in the Redis cache.

    :param key: The key to set in the cache.
    :param value: The value to set in the cache.
    :param timeout: The time (in seconds) to keep the value in the cache (default is 15 minutes).
    """
    # Using the Redis client to set the value with an expiration
    r.setex(key, timeout, value)

def get_value_view(request):
    value = r.get(request)  # Use the Redis client to get the value directly

    if value:
        return {'key': request, 'value': value}
    return None

