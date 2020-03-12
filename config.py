# -*- config:utf-8 -*-

import logging
from datetime import timedelta
import os


class Config(object):
    # Base path
    APPLICATION_PATH = os.path.dirname(os.path.abspath(__file__))

    USE_X_SENDFILE = False

    # DATABASE CONFIGURATION
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CSRF_ENABLED = True
    WTF_CSRF_ENABLED = True

    # LOGGING
    LOG_LEVEL = logging.INFO

    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)

    # ex: BLUEPRINTS = ['blog']  # where app is a Blueprint instance
    # ex: BLUEPRINTS = [('blog', {'url_prefix': '/myblog'})]  # where app is a Blueprint instance

    BLUEPRINTS = [
        # ('base'),
        ('ganalytics', {'url_prefix': '/v<int:api_version>/t'}),  # noqa
        ('accounts',   {'url_prefix': '/v<int:api_version>/account'}),  # noqa
        ('auth',       {'url_prefix': '/v<int:api_version>/auth'}),  # noqa
        ('webhooks',   {'url_prefix': '/v<int:api_version>/webhooks'}),  # noqa | For handling webhook events like Stripe or CustomerIO
    ]


class Testing(Config):
    TESTING = True
    ENV = 'Testing'
    DEBUG = True

    SQLALCHEMY_DATABASE_URI = "mysql://root:root@127.0.0.1/pdfshift_test?charset=utf8"
    SESSION_COOKIE_SECURE = False
    SENTRY_DSN = None
    REDIS_URL = "redis://localhost:6379"
