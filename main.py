# -*- coding:utf-8 -*-

import os, sys, logging

from werkzeug import import_string
from flask import Flask, render_template, send_from_directory, request, make_response

# apps is a special folder where you can place your blueprints
PROJECT_PATH = os.path.abspath(os.path.dirname(__file__))
sys.path.insert(0, os.path.join(PROJECT_PATH, "apps"))


def __import_variable(blueprint_path, module, variable_name):
    path = '.'.join(blueprint_path.split('.') + [module])
    mod = __import__(path, fromlist=[variable_name])
    return getattr(mod, variable_name)


def app_factory(config, app_name=None, blueprints=None):
    app_name = app_name or __name__
    app = Flask(app_name, static_url_path="/public")

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
    app.config.from_envvar("APP_CONFIG", silent=True)  # available in the server


def configure_logger(app, config):
    if not app.debug:
        # Create a file logger since we got a logdir
        stream_handler = logging.StreamHandler()
        formatter = logging.Formatter(config.LOG_FORMAT)
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
    def forbidden_page(error):
        """
        The server understood the request, but is refusing to fulfill it.
        Authorization will not help and the request SHOULD NOT be repeated.
        If the request method was not HEAD and the server wishes to make public
        why the request has not been fulfilled, it SHOULD describe the reason for
        the refusal in the entity. If the server does not wish to make this
        information available to the client, the status code 404 (Not Found)
        can be used instead.
        """
        return make_response(render_template("errors/403.html"), 403)
        # return make_response(jsonify({'error': 'Access Forbidden.', 'code': 403}), 403)

    @app.errorhandler(404)
    def page_not_found(error):
        """
        The server has not found anything matching the Request-URI. No indication
        is given of whether the condition is temporary or permanent. The 410 (Gone)
        status code SHOULD be used if the server knows, through some internally
        configurable mechanism, that an old resource is permanently unavailable
        and has no forwarding address. This status code is commonly used when the
        server does not wish to reveal exactly why the request has been refused,
        or when no other response is applicable.
        """
        return make_response(render_template("errors/404.html"), 404)
        # return make_response(jsonify({'error': 'Page not found.', 'code': 404}), 404)

    @app.errorhandler(405)
    def method_not_allowed_page(error):
        """
        The method specified in the Request-Line is not allowed for the resource
        identified by the Request-URI. The response MUST include an Allow header
        containing a list of valid methods for the requested resource.
        """
        return make_response(render_template("errors/404.html"), 405)
        # return make_response(jsonify({'error': 'Method not allowed.', 'code': 405}), 405)

    @app.errorhandler(410)
    def request_gone(e):
        return make_response(jsonify({'error': 'Gone.', 'code': 410}), 410)

    if app.debug:
        return

    @app.errorhandler(500)
    @app.errorhandler(Exception)
    def server_error_page(error):
        app.logger.exception(e)
        return make_response(render_template("errors/500.html"), 500)
        # return make_response(jsonify({'error': 'Internal server error. We were notified!', 'code': 500}), 500)


def configure_database(app):
    """
    Database configuration should be set here
    """
    from database import db
    db.app = app
    db.init_app(app)

    from flask_migrate import Migrate
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
    pass


def configure_views(app):
    """Add some simple views here like index_view"""

    @app.route('/robots.txt')
    @app.route('/sitemap.xml')
    def static_from_root():
        return send_from_directory(app.static_folder, request.path[1:])

    #for rule in app.url_map.iter_rules():
    #    print rule
