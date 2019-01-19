import os

from redis import StrictRedis
import json


def get_redis_client():
    return StrictRedis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)


redis_client = get_redis_client()


def get_from_general_cache(key):
    return redis_client.get(key)


def store_in_general_cache(key, result, timeout=300):
    redis_client.set(key, result)
    redis_client.expire(key, timeout)


def consider_cache(key, method_to_invoke, *args):
    content = get_from_general_cache(key)
    if content is None:
        if args:
            results = method_to_invoke(*args)
        else:
            results = method_to_invoke()
        content = json.dumps(results)
        store_in_general_cache(key, content)
    return content
