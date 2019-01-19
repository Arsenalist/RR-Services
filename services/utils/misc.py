import base64
import hashlib
import os
from urllib.parse import urlparse

from redis import StrictRedis

from services.utils.httputils import HttpUtils

def get_redis_client():
    return StrictRedis.from_url(os.environ.get("REDIS_URL"), decode_responses=True)

redis_client = get_redis_client()

def get_from_general_cache(key):
    return redis_client.get(key)


def store_in_general_cache(key, result, timeout=300):
    redis_client.set(key, result)
    redis_client.expire(key, timeout)


def considerCache(endpoint, timeout=600):
    key = hashlib.md5(endpoint.encode()).hexdigest()
    result = get_from_general_cache(key)
    if (result is None):
        result = HttpUtils.make_request(endpoint)
        if (key is not None and result is not None):
            store_in_general_cache(key, result, timeout)
    return result


def remove_attrs(soup):
    for tag in soup.findAll(True):
        tag.attrs = None
    return soup


def decorate_table_with_material_design(content):
    replacements = [
        {
        'target': 'class="suppress_glossary sortable stats_table"',
        'replacement': 'role="grid" class="mat-table"'
        },
        {
        'target': '<table ',
        'replacement': '<table role="grid" class="mat-table" '
        },
        {
        'target': '<td>',
        'replacement': '<td role="gridcell" class="mat-cell">'
        },
        {
        'target': '<th>',
        'replacement': '<th role="columnheader" class="mat-header-cell">'
        },
        {
        'target': '<tr>',
        'replacement': '<tr role="row" class="mat-row">'
        }
    ]
    for r in replacements:
        content = content.replace(r['target'], r['replacement'])
    return content


def findDomain(url):
    o = urlparse(url)
    return o.hostname


def sanitize_content(content):
    return content.replace("<amp-", "<").replace("</amp-", "</")


def encode_string(to_encode):
    return base64.b64encode(to_encode.encode()).decode('utf-8')


def decode_string(to_decode):
    return base64.b64decode(to_decode.encode('utf-8')).decode()


