# -*- config:utf-8 -*-

import logging
from datetime import timedelta
import os


class Config(object):
    # Base path
    APPLICATION_PATH = os.path.dirname(os.path.abspath(__file__))

    # use DEBUG mode?
    DEBUG = True

    # use TESTING mode?
    TESTING = False

    # use server x-sendfile?
    USE_X_SENDFILE = False

    # DATABASE CONFIGURATION
    SQLALCHEMY_DATABASE_URI = None
    SQLALCHEMY_ECHO = False
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    CSRF_ENABLED = True
    WTF_CSRF_ENABLED = True
    SECRET_KEY = ''  # import os; os.urandom(24)

    # LOGGING
    LOG_LEVEL = logging.INFO

    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)

    REDIS_NAMESPACE = ''
    REDIS_URL = 'redis://localhost:6379'

    CONTACT_NAME = ''
    CONTACT_EMAIL = ''

    SPARKPOST_KEY = None

    # ex: BLUEPRINTS = ['blog']  # where app is a Blueprint instance
    # ex: BLUEPRINTS = [('blog', {'url_prefix': '/myblog'})]  # where app is a Blueprint instance
    BLUEPRINTS = [
        # ('base'),
        ('example', {'url_prefix': '/example/'}),
    ]
