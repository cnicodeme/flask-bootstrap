# -*- config:utf-8 -*-

import logging
from datetime import timedelta
import os
from dotenv import Dotenv

dotenv = Dotenv(os.path.join(os.path.dirname(__file__), ".env"))
os.environ.update(dotenv)


class Config(object):
    # Base path
    APPLICATION_PATH = os.path.dirname(os.path.abspath(__file__))

    # use DEBUG mode?
    DEBUG = os.getenv('DEBUG', False)

    # use TESTING mode?
    TESTING = os.getenv('DEBUG_TESTING', False)

    # use server x-sendfile?
    USE_X_SENDFILE = False

    # DATABASE CONFIGURATION
    SQLALCHEMY_DATABASE_URI = os.getenv('DATABASE_URI', None)
    SQLALCHEMY_ECHO = os.getenv('DATABASE_DEBUG', False)

    CSRF_ENABLED = True
    WTF_CSRF_ENABLED = True
    SECRET_KEY = ''  # import os; os.urandom(24)

    # LOGGING
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = "%(asctime)s %(levelname)s\t: %(message)s"  # used by logging.Formatter

    SESSION_COOKIE_HTTPONLY = False
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = timedelta(days=1)

    CONTACT_NAME = ''
    CONTACT_EMAIL = ''

    # ex: BLUEPRINTS = ['blog']  # where app is a Blueprint instance
    # ex: BLUEPRINTS = [('blog', {'url_prefix': '/myblog'})]  # where app is a Blueprint instance
    BLUEPRINTS = [
        # ('base'),
        ('example', {'url_prefix': '/example/'}),
    ]
