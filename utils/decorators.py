# coding=utf-8

from flask import current_app, make_response, abort, jsonify, request, g
import time, functools, base64


def authenticated(func=None, level='bearer', limit=5):
    assert level in ('bearer', 'api')

    def _authenticated(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            try:
                auth = request.headers.get('Authorization', None)
                assert auth is not None
                if level == 'bearer':
                    assert auth[0:6].lower() == 'bearer'

                if auth[0:6].lower() == 'bearer':
                    """
                    Authorization: Bearer XXXXXXXX
                    Is for access from the web application
                    """
                    from auth.models import Session
                    session = Session.find_by_token(auth[7:])
                    assert session is not None
                    g.account = session.account
                elif auth[0:5].lower() == 'basic':
                    """
                    Authorization: Basic sk_xxxxxx
                    Is for access from the API
                    """

                    passwd = None
                    if auth[6:8] == 'sk':
                        passwd = auth[6:]
                    else:
                        try:
                            credentials = base64.b64decode(auth[6:].encode('utf-8')).decode('utf-8')
                        except Exception:
                            raise AssertionError('Invalid credential provided')

                        assert credentials.find(':') > -1
                        assert credentials.count(':') == 1
                        passwd = credentials.split(':')[1]  # Authorization : api:sk_xxxxx
                        assert passwd[0:2] == 'sk'

                    from accounts.models import ApiKey
                    account = ApiKey.account_by_token(passwd)
                    assert account is not None
                    g.account = account
            except AssertionError as e:
                print(e)
                abort(401)

            remote_addr = request.remote_addr
            if request.headers.getlist("X-Forwarded-For"):
                remote_addr = request.headers.getlist("X-Forwarded-For")[0]

            key = 'rate-limit/{0}/{1}'.format(remote_addr, request.endpoint)
            ratelimit = RateLimit(key, limit)
            g._view_rate_limit = ratelimit
            if ratelimit.over_limit:
                return make_response(jsonify({
                    'success': False,
                    'error': 'You have been rate limited. Please wait {0} seconds.'.format(ratelimit.reset - int(time.time())),
                    'code': 429
                }), 429)

            if auth[0:5].lower() != 'basic' and g.get('_ga') is not None:
                g._ga.set_uid(g.account.uuid)

            return view_func(*args, **kwargs)

        return wrapper

    if func:
        return _authenticated(func)

    return _authenticated


def ratelimit(func=None, limit=5):
    def _ratelimit(view_func):
        @functools.wraps(view_func)
        def wrapper(*args, **kwargs):
            remote_addr = request.remote_addr
            if request.headers.getlist("X-Forwarded-For"):
                remote_addr = request.headers.getlist("X-Forwarded-For")[0]

            key = 'rate-limit/{0}/{1}'.format(remote_addr, request.endpoint)
            ratelimit = RateLimit(key, limit)
            g._view_rate_limit = ratelimit
            if ratelimit.over_limit:
                return make_response(jsonify({
                    'success': False,
                    'error': 'You have been rate limited. Please wait {0} seconds.'.format(ratelimit.reset - int(time.time())),
                    'code': 429
                }), 429)

            return view_func(*args, **kwargs)

        return wrapper

    if func:
        return _ratelimit(func)

    return _ratelimit


class RateLimit(object):
    expiration_window = 10

    def __init__(self, key_prefix, limit):
        """
        limit: int - Number of request per minutes
        """
        self.reset = (int(time.time()) // 60) * 60 + 60
        self.key = key_prefix + str(self.reset)
        self.limit = limit + 1
        if hasattr(current_app, 'redis_queue'):
            p = current_app.redis_queue.pipeline()
            p.incr(self.key)
            p.expireat(self.key, self.reset + self.expiration_window)
            self.current = min(p.execute()[0], self.limit)
        else:
            self.current = 0

    remaining = property(lambda x: x.limit - x.current)
    over_limit = property(lambda x: x.current >= x.limit)
