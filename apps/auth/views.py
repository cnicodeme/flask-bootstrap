# -*- coding:utf-8 -*-

from flask import Blueprint, request, jsonify
from utils.decorators import ratelimit
from auth.forms import AuthForm, LostPasswordForm
from accounts.models import Account
from auth.models import Session

app = Blueprint('auth', __name__)


@app.route("/login", methods=['POST'])
@ratelimit
def login():
    """
    Authenticate the user via the provided login/password
    """
    form = AuthForm.load(request)
    form.validate()

    account = Account.find_by_email(form.email.data)
    if not account:
        form.error('email', 'Invalid email/password credentials provided.')

    if not account.verify_password(form.password.data):
        form.error('email', 'Invalid email/password credentials provided.')

    ot = Session(account.id).save(True)
    return jsonify({
        'success': True,
        'token': ot.token,
        'account': account.serialize()
    })


@app.route("/lost-password", methods=['POST'])
@ratelimit
def lost_password():
    """
    Send a one time login link to authenticate the user.
    The link will contain an Session token that can be used directly from the app.
    """
    form = LostPasswordForm.load(request)
    form.validate()

    account = Account.find_by_email(form.email.data)
    if account:
        ot = Session(account.id)
        ot.save(True)
        ot.send()

    return jsonify({
        'success': True
    })
