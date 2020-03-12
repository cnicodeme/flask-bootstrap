# -*- coding:utf-8 -*-

from werkzeug.utils import import_string
from flask import Flask, request, make_response, jsonify, abort, g
from werkzeug.exceptions import HTTPException
from werkzeug.routing import RequestRedirect
from config import Config
from logging.handlers import SysLogHandler
import os, sys, logging, socket

try:
    import sentry_sdk
    from sentry_sdk.integrations.flask import FlaskIntegration
except ImportError:
    pass


# apps is a special folder where you can place your blueprints
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_PATH, "apps"))


def __import_variable(blueprint_path, module, variable_name):
    path = '.'.join(blueprint_path.split('.') + [module])
    mod = __import__(path, fromlist=[variable_name])
    return getattr(mod, variable_name)


class _ContextFilter(logging.Filter):
    hostname = socket.gethostname()

    def filter(self, record):
        record.hostname = self.hostname
        return True


def app_factory(app_name=None, blueprints=None, config=None):
    app_name = app_name or __name__
    app = Flask(app_name, static_url_path="/public")

    if not config:
        config = Config

    configure_app(app, config)
    configure_logger(app, config)
    configure_blueprints(app, blueprints or config.BLUEPRINTS)
    configure_error_handlers(app)
    configure_database(app)
    configure_context_processors(app)
    configure_template_filters(app)
    configure_extensions(app)
    configure_before_after_request(app)
    configure_views(app)

    return app


def configure_app(app, config):
    """Loads configuration class into flask app"""
    app.config.from_object(config)
    app.config.from_pyfile(".env", silent=True)  # available in the server


def configure_logger(app, config):
    if not app.debug:
        if app.config.get('SENTRY_DSN', None) is not None:
            sentry_sdk.init(app.config.get('SENTRY_DSN'), integrations=[FlaskIntegration()])

        if app.config.get('PAPERTRAIL_HOST', None):
            syslog = SysLogHandler(address=(
                app.config.get('PAPERTRAIL_HOST'),
                int(app.config.get('PAPERTRAIL_PORT'))
            ))
            formatter = logging.Formatter(
                '%(asctime)s %(hostname)s: %(levelname)s %(message)s',
                datefmt='%b %d %H:%M:%S'
            )
            syslog.setFormatter(formatter)
            syslog.setLevel(logging.WARNING)
            syslog.addFilter(_ContextFilter())
            app.logger.addHandler(syslog)

        # Create a file logger since we got a logdir
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter("%(asctime)s %(levelname)s\t: %(message)s")
        stream_handler.setFormatter(formatter)
        app.logger.addHandler(stream_handler)

        app.logger.setLevel(config.LOG_LEVEL)

    app.logger.info("Logger started")


def configure_blueprints(app, blueprints):
    """Registers all blueprints set up in config.py"""
    for blueprint_config in blueprints:
        blueprint, kw = None, {}

        if isinstance(blueprint_config, str):
            blueprint = blueprint_config
        elif isinstance(blueprint_config, tuple):
            blueprint = blueprint_config[0]
            kw = blueprint_config[1]
        else:
            print("Error in BLUEPRINTS setup in config.py")
            print("Please, verify if each blueprint setup is either a string or a tuple.")
            exit(1)

        blueprint = __import_variable(blueprint, 'views', 'app')
        if isinstance(blueprint, tuple):
            for bp in blueprint:
                app.register_blueprint(bp, **kw)
        else:
            app.register_blueprint(blueprint, **kw)


def configure_error_handlers(app):
    @app.errorhandler(HTTPException)
    def handle_http_exception(e):
        if isinstance(e, RequestRedirect):
            if '{0}/'.format(request.url) == e.new_url:
                # In case of a slash redirect, we return a 404 instead to avoid confusion
                return make_response(jsonify({'success': False, 'error': str('Page not found'), 'code': 404}), 404)

            return e.get_response(None)

        response = e.get_response(None)
        if response.headers.get('content-type') == 'application/json':
            return response

        return make_response(jsonify({'success': False, 'error': str(e), 'code': e.code}), e.code)

    if app.debug:
        return

    @app.errorhandler(500)
    @app.errorhandler(Exception)
    def server_error_page(error):
        if hasattr(error, 'get_response'):
            return handle_http_exception(error)

        app.logger.exception(error)
        output = {
            'success': False,
            'error': 'Internal server error. We were notified!',
            'code': 500
        }

        return make_response(jsonify(output), 500)


def configure_database(app):
    """
    Database configuration should be set here
    """
    from database import db
    from flask_migrate import Migrate

    db.app = app
    db.init_app(app)
    Migrate(app, db)


def configure_context_processors(app):
    """Modify templates context here"""
    pass


def configure_template_filters(app):
    """Configure filters and tags for jinja"""

    app.jinja_env.filters['nl2br'] = import_string('utils.templates.nl2br')
    app.jinja_env.filters['dateformat'] = import_string('utils.templates.dateformat')
    app.jinja_env.filters['timeformat'] = import_string('utils.templates.timeformat')
    app.jinja_env.filters['datetimeformat'] = import_string('utils.templates.datetimeformat')
    app.jinja_env.filters['price'] = import_string('utils.templates.price')


def configure_extensions(app):
    """Configure extensions like mail and login here"""
    if app.config.get('REDIS_URL', None) is not None:
        from utils.queue import RedisQueue
        app.redis_queue = RedisQueue(app.config.get('REDIS_NAMESPACE'), app.config.get('REDIS_URL'))


def configure_before_after_request(app):
    @app.url_defaults
    def define_api_version(endpoint, values):
        if 'api_version' in values:
            # We can force from the call, in which case we don't change it
            return

        if not app.url_map.is_endpoint_expecting(endpoint, 'api_version'):
            # If the endpoint doesn't expect a version, we don't add it
            return

        values['api_version'] = g.get('api_version', 3)

    @app.url_value_preprocessor
    def append_api_version(endpoint, values):
        if endpoint is not None and 'api_version' in values:
            api_version = int(values.get('api_version'))

            """
            if api_version not in (2, 3):
                abort(404)
            """

            values.pop('api_version', None)
            g.api_version = api_version

    @app.after_request
    def after_request_cors(response):
        """ Implementing CORS """
        h = response.headers
        h.add('Access-Control-Allow-Origin', '*')
        h.add('Access-Control-Allow-Methods', 'HEAD, GET, POST, PUT, DELETE, OPTIONS')
        h.add('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Host, Authorization')

        return response

    @app.after_request
    def inject_x_rate_headers(response):
        limit = getattr(g, '_view_rate_limit', None)
        if limit is not None:
            h = response.headers
            h.add('X-RateLimit-Remaining', str(limit.remaining))
            h.add('X-RateLimit-Limit', str(limit.limit))
            h.add('X-RateLimit-Reset', str(limit.reset))
        return response


def configure_views(app):
    """Add some simple views here like index_view"""

    @app.route('/ping')
    def ping():
        return 'Pong ({} v1)'.format(app.config.get('APPLICATION_NAME'))

    """
    for rule in app.url_map.iter_rules():
        print(rule)
    """
