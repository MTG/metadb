from functools import update_wrapper, wraps
from datetime import timedelta
from flask import request, current_app, make_response
from six import string_types
from werkzeug.exceptions import Unauthorized

from metadb import data


def _get_token_from_header(header):
    token = {}
    if header:
        parts = header.split(" ")
        if len(parts) == 2 and parts[0] == "Token":
            token = data.get_token(parts[1])
    return token


def auth_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization")
        token = _get_token_from_header(auth)
        if token:
            return f(*args, **kwargs)
        raise Unauthorized
    return decorated


def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.headers.get("Authorization")
        token = _get_token_from_header(auth)
        if token and token["admin"]:
            return f(*args, **kwargs)
        raise Unauthorized

    return decorated


def crossdomain(origin='*', methods=None, headers=None,
                max_age=21600, attach_to_all=True,
                automatic_options=True):
    # Based on snippet by Armin Ronacher located at http://flask.pocoo.org/snippets/56/.
    if methods is not None:
        methods = ', '.join(sorted(x.upper() for x in methods))
    if headers is not None and not isinstance(headers, string_types):
        headers = ', '.join(x.upper() for x in headers)
    if not isinstance(origin, string_types):
        origin = ', '.join(origin)
    if isinstance(max_age, timedelta):
        max_age = max_age.total_seconds()

    def get_methods():
        if methods is not None:
            return methods

        options_resp = current_app.make_default_options_response()
        return options_resp.headers['allow']

    def decorator(f):
        def wrapped_function(*args, **kwargs):
            if automatic_options and request.method == 'OPTIONS':
                resp = current_app.make_default_options_response()
            else:
                resp = make_response(f(*args, **kwargs))
            if not attach_to_all and request.method != 'OPTIONS':
                return resp

            h = resp.headers

            h['Access-Control-Allow-Origin'] = origin
            h['Access-Control-Allow-Methods'] = get_methods()
            h['Access-Control-Max-Age'] = str(max_age)
            if headers is not None:
                h['Access-Control-Allow-Headers'] = headers
            return resp

        f.provide_automatic_options = False
        return update_wrapper(wrapped_function, f)
    return decorator

