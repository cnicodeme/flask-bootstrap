# -*- coding:utf-8 -*-

from werkzeug import import_string
from flask import Flask, request, make_response, jsonify, send_from_directory
from werkzeug.exceptions import HTTPException
from config import Config
from utils.queue import RedisQueue
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


def app_factory(app_name=None, blueprints=None):
    app_name = app_name or __name__
    app = Flask(app_name, static_url_path="/public")

    configure_app(app, Config)
    configure_logger(app, Config)
    configure_blueprints(app, blueprints or Config.BLUEPRINTS)
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
    def _handle_http_exception(e):
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
            return _handle_http_exception(error)

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


def configure_extensions(app):
    """Configure extensions like mail and login here"""
    if app.config.get('REDIS_NAMESPACE', None) is not None:
        app.redis_queue = RedisQueue(app.config.get('REDIS_NAMESPACE'), app.config.get('REDIS_URL'))


def configure_before_after_request(app):
    @app.after_request
    def after_request_cors(response):
        """ Implementing CORS """
        h = response.headers
        h.add('Access-Control-Allow-Origin', '*')
        h.add('Access-Control-Allow-Methods', 'HEAD, GET, POST, PUT, DELETE, OPTIONS')
        h.add('Access-Control-Allow-Headers', 'Origin, X-Requested-With, Content-Type, Accept, Host, Authorization')

        return response


def configure_views(app):
    """Add some simple views here like index_view"""

    @app.route('/robots.txt')
    @app.route('/sitemap.xml')
    def static_from_root():
        return send_from_directory(app.static_folder, request.path[1:])

    # for rule in app.url_map.iter_rules():
    #    print(rule)
