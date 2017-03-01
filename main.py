# -*- coding:utf-8 -*-

from werkzeug import import_string
from flask import Flask, request, make_response, jsonify, send_from_directory
from config import Config
import os, sys, logging


# apps is a special folder where you can place your blueprints
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_PATH, "apps"))


def __import_variable(blueprint_path, module, variable_name):
    path = '.'.join(blueprint_path.split('.') + [module])
    mod = __import__(path, fromlist=[variable_name])
    return getattr(mod, variable_name)


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

        if isinstance(blueprint_config, basestring):
            blueprint = blueprint_config
        elif isinstance(blueprint_config, tuple):
            blueprint = blueprint_config[0]
            kw = blueprint_config[1]
        else:
            print "Error in BLUEPRINTS setup in config.py"
            print "Please, verify if each blueprint setup is either a string or a tuple."
            exit(1)

        blueprint = __import_variable(blueprint, 'views', 'app')
        if isinstance(blueprint, tuple):
            for bp in blueprint:
                app.register_blueprint(bp, **kw)
        else:
            app.register_blueprint(blueprint, **kw)


def configure_error_handlers(app):
    @app.errorhandler(401)
    def authorization_required(e):
        return make_response(jsonify({'error': 'Authorization required.', 'code': 401}), 401)

    @app.errorhandler(403)
    def access_forbidden(e):
        return make_response(jsonify({'error': 'Access Forbidden.', 'code': 403}), 403)

    @app.errorhandler(404)
    def page_not_found(e):
        return make_response(jsonify({'error': 'Page not found.', 'code': 404}), 404)

    @app.errorhandler(405)
    def method_not_allowed(e):
        return make_response(jsonify({'error': 'Method not allowed.', 'code': 405}), 405)

    @app.errorhandler(410)
    def request_gone(e):
        return make_response(jsonify({'error': 'Gone.', 'code': 410}), 410)

    if app.debug:
        return

    @app.errorhandler(500)
    @app.errorhandler(Exception)
    def server_error_page(error):
        app.logger.exception(error)
        return make_response(jsonify({'error': 'Internal server error. We were notified!', 'code': 500}), 500)


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
    pass


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
    #    print rule
