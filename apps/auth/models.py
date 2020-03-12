# -*- coding:utf-8 -*-

from flask import current_app, request
from database import db
from sqlalchemy import text
from sqlalchemy.orm import relationship, backref
from utils.models import ORModel
from utils.mailer import Mailgun
from urllib.parse import urlparse
import datetime, uuid


class Session(db.Model, ORModel):
    __tablename__ = 'sessions'

    id         = db.Column(db.Integer, primary_key=True)

    expires    = db.Column(db.DateTime, index=True)
    token      = db.Column(db.String(100), nullable=False, unique=True, index=True)

    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    account    = relationship('Account', backref=backref('sessions'))

    def __init__(self, account_id):
        self.account_id = account_id
        self.expires = datetime.datetime.utcnow() + datetime.timedelta(days=30)
        self.token = str(uuid.uuid4()).replace('-', '')
        self.clear()

    def send(self):
        if current_app.debug:
            print('Login link: {0}'.format(self.get_link()))
        else:
            # CustomerIO.event(self.account_id, 'login_link', {'link': self.get_link()})
            mail = Mailgun("Your {} access".format(current_app.config.get('APPLICATION_NAME')), "auth/one-time")
            mail.send(self.account, {'link': self.get_link()})

    def get_link(self):
        base_url = None
        if current_app.debug:
            if request.headers.get('referer'):
                referer = urlparse(request.headers.get('referer'))
                base_url = '{0}://{1}'.format(referer.scheme, referer.netloc)
            else:
                base_url = 'http://127.0.0.1:8080'
        else:
            base_url = 'https://{}'.format(current_app.config.get('APPLICATION_URL'))

        return base_url + '/auth/{0}'.format(self.token)

    def clear(self):
        """
        We delete the previously created tokens that where created more than 4 hour ago
        (in case the user request multiple tokens because of mail lagging)
        """
        db.engine.execute(text('DELETE FROM sessions WHERE account_id = :account AND expires < (UTC_TIMESTAMP() + INTERVAL 1 MONTH - INTERVAL 4 HOUR)'), account=self.account_id)

    @classmethod
    def find_by_token(cls, token):
        return cls.query.filter(cls.expires > datetime.datetime.utcnow()).filter(cls.token == token).first()
