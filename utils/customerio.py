# -*- coding:utf-8 -*-

from flask import current_app
from sentry_sdk import capture_exception
import requests


class CustomerIO(object):
    @classmethod
    def _request(cls, method, url, data=None, silent=False):
        if current_app.debug:
            print("Sending {0} request to {1} with {2}".format(method, url, data))

        if not current_app.config.get('CUSTOMERIO_API_KEY', None):
            return None

        r = getattr(requests, method)(
            'https://track.customer.io/api/v1{0}'.format(url),
            auth=(current_app.config.get('CUSTOMERIO_SITE_ID'), current_app.config.get('CUSTOMERIO_API_KEY')),
            json=data,
            timeout=3
        )

        try:
            r.raise_for_status()
            return r
        except Exception as e:
            if not silent:
                capture_exception(e)

    @classmethod
    def account(cls, account_id, params):
        return cls._request('put', '/customers/{0}'.format(account_id), params)

    @classmethod
    def event(cls, account_id, name, params=None):
        event = {'name': name, 'data': {}}
        if params:
            event['data'] = params

        return cls._request('post', '/customers/{0}/events'.format(account_id), event)

    @classmethod
    def remove(cls, account_id):
        return cls._request('post', '/customers/{0}/suppress'.format(account_id))
