from django.http import JsonResponse
import redis

# Create a Redis client instance
r = redis.Redis(
    host='redis-18686.c257.us-east-1-3.ec2.redns.redis-cloud.com',
    port=18829,
    password='BC17yZIMp2B1FmuZnVGO2sGSAdTcznVt',
    decode_responses=True  # This will decode the responses to strings
)

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

