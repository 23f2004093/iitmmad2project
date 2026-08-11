import redis

import json

import functools

from flask import request, jsonify



try:

    r = redis.Redis(host="localhost", port=6379, db=0, decode_responses=True)

except Exception:

    r = None



def cache_get(key):

    if not r:

        return None

    try:

        val = r.get(key)

        return json.loads(val) if val else None

    except Exception:

        return None



def cache_set(key, value, timeout=60):

    if not r:

        return

    try:

        r.setex(key, timeout, json.dumps(value))

    except Exception:

        pass



def cache_clear_pattern(pattern):

    if not r:

        return

    try:

        keys = r.keys(pattern)

        if keys:

            r.delete(*keys)

    except Exception:

        pass



def cached_api(key_prefix, timeout=60):

    def decorator(f):

        @functools.wraps(f)

        def decorated_function(*args, **kwargs):

            cache_key = f"{key_prefix}:{request.path}:{request.query_string.decode('utf-8')}"

            cached_data = cache_get(cache_key)

            if cached_data is not None:

                return jsonify(cached_data), 200

            response = f(*args, **kwargs)

            if isinstance(response, tuple) and len(response) == 2:

                data_obj, status_code = response

                if status_code == 200:

                    raw_data = data_obj.get_json() if hasattr(data_obj, 'get_json') else data_obj

                    cache_set(cache_key, raw_data, timeout)

            return response

        return decorated_function

    return decorator
