# -*- coding:utf-8 -*-

from flask import Blueprint, request, current_app, make_response, jsonify
from accounts.models import Account
import hmac, hashlib


app = Blueprint('webhooks', __name__)


@app.route('/customerio', methods=['POST'])
def customerio():
    if request.headers.get('x-cio-timestamp', '') == '':
        return make_response(jsonify({
            'success': False,
            'reason': 'Invalid request made.'
        }), 400)

    payload = b'v0:' + request.headers.get('x-cio-timestamp').encode() + b':' + request.get_data()

    signature = hmac.new(
        key=current_app.config.get('CUSTOMERIO_SIGNING_KEY').encode(),
        msg=payload,
        digestmod=hashlib.sha256).hexdigest()

    if signature != request.headers.get('x-cio-signature'):
        return make_response(jsonify({
            'success': False,
            'reason': 'Invalid request made.'
        }), 400)

    body = request.get_json()
    assert body.get('event_type') == 'email_bounced'
    account = Account.find_by_email(body.get('data').get('email_address'))
    if account is None:
        return 'ok'

    account.lock('bounced')
    account.save(True)

    return 'ok'
