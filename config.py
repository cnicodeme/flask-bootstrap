# -*- config:utf-8 -*-

import logging
from datetime import timedelta
import os

project_name = "my_project"


class Config(object):
    # Base path
    APPLICATION_PATH = os.path.dirname(os.path.abspath(__file__))

    # use DEBUG mode?
    DEBUG = False

    # use TESTING mode?
    TESTING = False

    # use server x-sendfile?
    USE_X_SENDFILE = False

    # DATABASE CONFIGURATION
    SQLALCHEMY_DATABASE_URI = "mysql://login:password@127.0.0.1/database?charset=utf8"
    SQLALCHEMY_ECHO = False

    CSRF_ENABLED = True
    WTF_CSRF_ENABLED = True
    SECRET_KEY = '' # import os; os.urandom(24)

    # LOGGING
    LOGGER_NAME = "%s_log" % project_name
    LOG_FILENAME = "%s.log" % project_name
    LOG_LEVEL = logging.INFO
    LOG_FORMAT = "%(asctime)s %(levelname)s\t: %(message)s" # used by logging.Formatter

    PERMANENT_SESSION_LIFETIME = timedelta(days=1)

    # EMAIL CONFIGURATION
    MAIL_SERVER = "smtp.mandrillapp.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False
    MAIL_DEBUG = False
    MAIL_USERNAME = 'email'
    MAIL_PASSWORD = 'api_password'

    # Used in main.py for Mail logging
    MAIL_ERROR_SOURCE = 'errors@project.com'
    MAIL_ERROR_DEST = ['admins@project.com',] # Must be a list
    MAIL_ERROR_SUBJECT = '[My Project] - An error occured.'

    # ex: BLUEPRINTS = ['blog']  # where app is a Blueprint instance
    # ex: BLUEPRINTS = [('blog', {'url_prefix': '/myblog'})]  # where app is a Blueprint instance
    BLUEPRINTS = [
        #('base'),
        ('example', {'url_prefix': '/example/'}),
    ]

class Prod(Config):
    pass


class Dev(Config):
    SQLALCHEMY_DATABASE_URI = "mysql://root:root@127.0.0.1/meels?charset=utf8"

    DEBUG = True
    MAIL_DEBUG = True
    SQLALCHEMY_ECHO = False

    # EMAIL CONFIGURATION
    MAIL_SERVER = "127.0.0.1"
    MAIL_PORT = 25
    MAIL_USE_TLS = False
    MAIL_USE_SSL = False
    MAIL_USERNAME = None
    MAIL_PASSWORD = None


class Testing(Config):
    TESTING = True
    CSRF_ENABLED = False
    WTF_CSRF_ENABLED = False
    SQLALCHEMY_DATABASE_URI = "sqlite:////tmp/%s_test.sqlite" % project_name
    SQLALCHEMY_ECHO = False
