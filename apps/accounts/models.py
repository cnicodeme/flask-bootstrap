# -*- coding:utf-8 -*-

from flask import current_app, request
from database import db
from sqlalchemy import text
from sqlalchemy.orm import relationship, backref
from utils.models import ORModel, JsonSerializable
from utils.countries import get_country_name
from utils.mailer import Mailgun
from urllib.parse import urlparse
import datetime, uuid, bcrypt


class Account(db.Model, ORModel, JsonSerializable):
    __tablename__     = 'accounts'
    __jsonserialize__ = ['name', 'email', 'company_name', 'company_details', 'company_vat',
                         'get_country_display', 'country', 'created', 'locked', 'lock_reason']

    id               = db.Column(db.Integer, primary_key=True)
    uuid             = db.Column(db.String(250), nullable=False, index=True, unique=True)  # Used mostly for Google Analytics or many other API

    name             = db.Column(db.String(250), nullable=True, default=None)
    email            = db.Column(db.String(250), nullable=False, index=True, unique=True)
    password         = db.Column(db.String(250), nullable=True, default=None)

    company_name     = db.Column(db.String(250), nullable=True, default=None)
    company_details  = db.Column(db.String(250), nullable=True, default=None)
    company_vat      = db.Column(db.String(250), nullable=True, default=None)
    country          = db.Column(db.String(2), nullable=True, default=None)

    created          = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    removed          = db.Column(db.DateTime, nullable=True, default=None)

    # stripe_id        = db.Column(db.String(250), nullable=True, index=True)

    locked           = db.Column(db.DateTime, nullable=True, default=None)
    lock_reason      = db.Column(db.String(250), nullable=True, default=None)

    def __init__(self):
        self.locked = datetime.datetime.utcnow()
        self.lock_reason = 'email'

    def __repr__(self):
        if self.name:
            return self.name.capitalize()

        return self.email.split('@')[0].replace('-', ' ').replace('+', ' ').replace('_', ' ').replace('.', ' ').capitalize()

    def get_firstname(self):
        current_name = str(self)
        if current_name and current_name.find(' ') > -1:
            return current_name.split(' ')[0]

        return current_name

    def has_password(self):
        return self.password is not None

    def set_password(self, password):
        if password is not None:
            self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt(12)).decode('utf-8')

    def verify_password(self, password):
        if self.password is None:
            return False

        if password is None:
            return False

        if isinstance(password, str):
            try:
                password = password.encode('utf-8')
            except UnicodeEncodeError:
                return False

        return bcrypt.checkpw(password, self.password.encode('utf-8'))

    def get_country_display(self):
        return get_country_name(self.country)

    def lock(self, reason):
        assert reason in ('ban', 'email', 'bounced')

        self.lock_reason = reason
        self.locked = datetime.datetime.utcnow()

    def unlock(self):
        self.lock_reason = None
        self.locked = None

    def save(self, commit=False):
        super().save(commit)
        # CustomerIO.account(self.id, self.serialize())

        """
        if self.stripe_id:
            Stripe.account(self)
        """

    def delete(self):
        Account.remove(self.id)

    @classmethod
    def find_by_email(cls, email):
        return cls.query.filter(cls.email == email).first()

    """
    @classmethod
    def find_by_stripe_id(cls, stripe_id):
        return cls.query.filter(cls.stripe_id == stripe_id).first()
    """

    @classmethod
    def remove(cls, account_id):
        db.engine.execute(text('DELETE FROM sessions WHERE account_id = :account'), account=account_id)
        db.engine.execute(text('DELETE FROM api_keys WHERE account_id = :account'), account=account_id)
        db.engine.execute(text('DELETE FROM account_emails WHERE account_id = :account'), account=account_id)

        # CustomerIO.remove(account_id)

        """
        stripe_row = db.engine.execute(text('SELECT stripe_id FROM accounts WHERE id = :account'), account=account_id).first()
        if stripe_row and stripe_row[0]:
            Stripe.cancel_subscriptions(stripe_row[0])

        payments = db.engine.execute(text('SELECT COUNT(id) FROM payments WHERE account_id = :account'), account=account_id).first()
        if int(payments[0]) > 0:
            db.engine.execute(text('UPDATE accounts SET removed = UTC_TIMESTAMP(), plan_id = NULL WHERE id = :account'), account=account_id)
        else:
            db.engine.execute(text('DELETE FROM accounts WHERE id = :account'), account=account_id)
        """
        db.engine.execute(text('DELETE FROM accounts WHERE id = :account'), account=account_id)


class ApiKey(db.Model, ORModel, JsonSerializable):
    __tablename__ = 'api_keys'
    __jsonserialize__ = ['created', 'removed', 'token']

    id            = db.Column(db.Integer, primary_key=True)
    created       = db.Column(db.DateTime, nullable=False, default=datetime.datetime.utcnow)
    removed       = db.Column(db.DateTime, nullable=True, default=None)
    token         = db.Column(db.String(250), nullable=False, unique=True, index=True)

    account_id    = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)

    def __init__(self, account_id):
        self.account_id = account_id
        self.created = datetime.datetime.utcnow()
        self.token = 'sk_{0}'.format(str(uuid.uuid4()).replace('-', ''))

    def disable(self):
        self.removed = datetime.datetime.utcnow()
        self.save(True)

    @classmethod
    def find_all(cls, account_id):
        return cls.query.filter(cls.account_id == account_id).order_by(cls.created.desc()).all()  # noqa

    @classmethod
    def count_active(cls, account_id):
        return ApiKey.query.filter(cls.account_id == account_id).filter(cls.removed == None).count()  # noqa

    @classmethod
    def account_by_token(cls, token):
        return Account.query.filter(Account.removed == None).join(ApiKey).filter(ApiKey.removed == None).filter(ApiKey.token == token).first()  # noqa

    @classmethod
    def find_by_token(cls, token):
        return ApiKey.query.filter(cls.token == token).first()  # noqa


class AccountEmail(db.Model, ORModel):
    __tablename__ = 'account_emails'

    id         = db.Column(db.Integer, primary_key=True)

    expires    = db.Column(db.DateTime, index=True)
    token      = db.Column(db.String(100), nullable=False, unique=True, index=True)
    email      = db.Column(db.String(250), nullable=False, index=True, unique=True)

    account_id = db.Column(db.Integer, db.ForeignKey('accounts.id'), nullable=False)
    account    = relationship('Account', backref=backref('emails'))

    def __init__(self, account_id, email):
        self.account_id = account_id
        self.email = email
        self.expires = datetime.datetime.utcnow() + datetime.timedelta(days=30)
        self.token = str(uuid.uuid4()).replace('-', '')

        self.clear()

    def validate(self):
        has_changes = False
        if self.account.email != self.email:
            self.account.email = self.email
            has_changes = True

        if self.account.lock_reason in ('email', 'bounced'):
            # When the lock is bounced, having the right link means it's not anymore
            self.account.unlock()
            has_changes = True

        if has_changes:
            self.account.save(True)

        # CustomerIO.event(self.account.id, 'validate_email_successful', {'email': self.email})
        self.delete(True)

    def send(self, updated=False):
        if current_app.debug:
            print('Login link: {0}'.format(self.get_link(updated)))
        else:
            # CustomerIO.event(self.account_id, 'validate_email', {'email': self.email, 'link': self.get_link(updated=updated)})
            mail = Mailgun("Validate your account", "account/{}".format('update' if updated else 'validate'))
            mail.send(self.account, {
                'link': self.get_link(updated)
            })

    def get_link(self, updated=False):
        base_url = None
        if current_app.debug:
            if request.headers.get('referer'):
                referer = urlparse(request.headers.get('referer'))
                base_url = '{0}://{1}'.format(referer.scheme, referer.netloc)
            else:
                base_url = 'http://127.0.0.1:8080'
        else:
            base_url = 'https://{}'.format(current_app.config.get('APPLICATION_URL'))

        if updated:
            return base_url + '/update/{}'.format(self.token)
        else:
            return base_url + '/validate/{}'.format(self.token)

    def clear(self):
        """
        We delete the previously created tokens that where created more than 4 hour ago
        (in case the user request multiple tokens because of mail lagging)
        """
        db.engine.execute(text('DELETE FROM sessions WHERE account_id = :account AND expires < (UTC_TIMESTAMP() + INTERVAL 1 MONTH - INTERVAL 4 HOUR)'), account=self.account_id)

    @classmethod
    def find_by_token(cls, token):
        return cls.query.filter(cls.expires > datetime.datetime.utcnow()).filter(cls.token == token).first()
