# -*- coding:utf-8 -*-

from flask import request, current_app
from random import random
import requests, hashlib


class Tracker(dict):
    """
    @see https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters
    """
    def __init__(self, ds='web'):
        self.v = 1
        self.tid = current_app.config.get('GOOGLE_ANALYTICS')  # UA-XXXX-Y
        self.aip = 1

        # Data source
        # https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters#ds
        self.ds = ds  # Data source: web, app

        # Cache buster, to avoid caching request
        # https://developers.google.com/analytics/devguides/collection/protocol/v1/parameters#z
        self.z = int(random() * 10**12)

        self.cid = None  # Client ID : Visitor
        self.uid = None  # User ID : When the user has created an account

        # Session control
        self.uip = None  # IP Override. Required since it's server side
        self.ua  = None  # UserAgent override

        # Traffic Sources
        self.dr = None  # Document referrer

        # System info
        self.sr = None  # Screen resolution
        self.vp = None  # Viewport size
        self.ul = None  # User language

        # Hit
        self.t  = None  # Hit type. Allowed: pageview, screenview, event, transaction, item, social, exception, timing
        self.dl = None  # URL where the hit occured
        self.dt = None  # Title of the page where the hit occured

        # Event tracking
        self.ec = None  # Category
        self.ea = None  # Action
        self.el = None  # Label
        self.ev = None  # Value

    def _load_from_request(self):
        self.ds = 'web'
        self.ds = 'web'
        remote_addr = request.remote_addr
        if request.headers.getlist("X-Forwarded-For"):
            remote_addr = request.headers.getlist("X-Forwarded-For")[0]

        try:
            response = requests.get('http://ip-api.com/json/{0}?fields=countryCode'.format(remote_addr))
            response.raise_for_status()
            self.geoid = response.json().get('countryCode')
        except Exception:
            self.uip = remote_addr

        self.ua = request.headers.get('user-agent')
        self.ul = request.accept_languages.best
        self.sr = request.args.get('sr', None)  # Screen resolution
        self.vp = request.args.get('vp', None)  # View port

        if request.cookies.get('_t'):
            self.cid = request.cookies.get('_t')

        if not self.cid:
            seq = '{0}-{1}-{2}-{3}-{4}'.format(self.uip, self.ua, self.ul, self.sr, self.vp)
            value = hashlib.sha1(seq.encode('utf-8', errors='replace')).hexdigest()
            self.cid = self._split_dash(value)

    def _split_dash(self, value):
        return '-'.join([value[i:i + 8] for i in range(0, len(value), 8)])

    def hit(self, hit, url, referer, title=None):
        if hit not in ('pageview', 'screenview', 'event', 'transaction', 'item', 'social', 'exception', 'timing'):
            raise ValueError('Invalid hit type!')

        self.t = hit
        self.dl = url
        self.dt = title
        self.dr = referer

    def event(self, category, action, label=None, value=None):
        self.t = 'event'
        self.ec = category
        self.ea = action
        self.el = label
        self.ev = value
        self.send()

    def set_uid(self, uid):
        value = hashlib.sha1('ga-{0}-{1}'.format(self.tid, uid).encode('utf-8')).hexdigest()
        self.uid = self._split_dash(value)

    def send(self):
        if self.tid is not None:
            try:
                requests.get('https://www.google-analytics.com/collect', params=self.__dict__).raise_for_status()
            except Exception as e:
                pass
