# -*- coding:utf-8 -*-

from jinja2 import evalcontextfilter, Markup
from flask import request
import cgi
import urllib

@evalcontextfilter
def nl2br(eval_ctx, value):
    if not value:
        return value

    # We use cgi because jinja2.escape doesn't seems to work correctly in our case
    value = cgi.escape(value, True)
    value = value.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '<br />')

    if eval_ctx.autoescape:
        value = Markup(value)

    return value

def dateformat(value, format = '%d/%m/%Y'):
    if not value:
        return ''

    return value.strftime(format)

def timeformat(value, format = '%H:%M:%S'):
    if not value:
        return ''

    return value.strftime(format)

def datetimeformat(value, format = '%d/%m/%Y %H:%M'):
    if not value:
        return ''

    return value.strftime(format.encode('utf-8')).decode('utf-8')
