import hashlib
import os

from redis import StrictRedis

from dataservices.utils.httputils import HttpUtils


def get_redis_client():
    return StrictRedis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)


redis_client = get_redis_client()


def get_from_general_cache(key):
    return redis_client.get(key)


def store_in_general_cache(key, result, timeout=300):
    redis_client.set(key, result)
    redis_client.expire(key, timeout)
