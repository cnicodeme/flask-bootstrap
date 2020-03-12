# -*- coding:utf-8 -*-

from flask import Blueprint, jsonify, g, request, abort
from utils.decorators import authenticated
from utils.countries import get_vat_details
from accounts.forms import AccountUpdateForm, CompanyVatForm, AccountPasswordForm
from accounts.models import Account, ApiKey, AccountEmail

app = Blueprint('accounts', __name__)


@app.route('/', methods=['GET'])
@authenticated(level='api')
def details():
    return jsonify(g.account.serialize())


@app.route('/', methods=['PUT'])
@authenticated
def update():
    form = AccountUpdateForm.load(request)
    form.validate()

    if form.email.data != g.account.email:
        if Account.find_by_email(form.email.data):
            form.error('email', 'This email is already used on our service.')

    updates = form.get_as_dict()
    pendingEmail = False
    if updates.get('email', None) and g.account.email != updates['email']:
        ae = AccountEmail(g.account.id, updates['email'])
        ae.save(True)
        ae.send(updated=True)
        del updates['email']
        pendingEmail = True

    if updates.get('company_vat'):
        try:
            details = get_vat_details(form.company_vat.data)
            if not updates.get('company_name') and not g.account.company_name:
                updates['company_name'] = details['name']

            if not updates.get('company_details') and not g.account.company_details:
                updates['company_details'] = details['address']

            if not updates.get('country') and not g.account.country:
                updates['country'] = details['countryCode']
        except Exception as e:
            form.error('company_vat', 'Invalid VAT provided.')

    g.account.update(**updates)
    g.account.save(True)

    return jsonify({
        'success': True,
        'pendingEmail': pendingEmail,
        'account': g.account.serialize()
    })


@app.route('/vat', methods=['POST'])
@authenticated(limit=5)
def vat_verify():
    form = CompanyVatForm.load(request)
    form.validate()

    try:
        details = get_vat_details(form.company_vat.data)
    except Exception as e:
        form.error('company_vat', str(e))

    if not details['valid']:
        form.error('company_vat', 'Invalid VAT number provided')

    return jsonify({
        'success': True,
        'details': details
    })


@app.route('/validate/', methods=['POST'])
@authenticated(limit=1)
def send_email_validation():
    """
    Sends an email to validate the account.
    Only if the account is locked because of "email" (upon creation only)
    """
    if g.account.lock_reason == 'email':
        ae = AccountEmail(g.account.id, g.account.email)
        ae.save(True)
        ae.send()

    return jsonify({
        'success': True
    })


@app.route('/validate/<token>', methods=['POST'])
def validate_email(token):
    ae = AccountEmail.find_by_token(token)
    if not ae:
        abort(404)

    body = request.get_json(silent=True)
    if not body:
        body = {}

    account_id = ae.account_id
    ae.validate()

    from auth.models import Session
    ot = Session(account_id).save(True)
    return jsonify({
        'success': True,
        'token': ot.token
    })


@app.route('/password', methods=['PUT'])
@authenticated
def update_password():
    form = AccountPasswordForm.load(request)
    form.validate()

    if not g.account.verify_password(form.current.data):
        form.error('current', 'Invalid password provided.')

    g.account.set_password(form.password.data)
    g.account.save(True)

    return jsonify({
        'success': True
    })


@app.route('/', methods=['DELETE'])
@authenticated
def delete_account():
    g.account.delete()
    return jsonify({'success': True})


@app.route('/api/')
@authenticated
def api_list():
    keys = ApiKey.find_all(g.account.id)
    if not keys:
        return jsonify({'success': True, 'keys': []})

    return jsonify({
        'success': True,
        'keys': [x.serialize() for x in keys]
    })


@app.route('/api/', methods=['POST'])
@authenticated
def api_key_create():
    if ApiKey.count_active(g.account.id) >= 3:
        return jsonify({
            'success': False,
            'errors': {
                'key': ['You cannot have more than 3 active keys.']
            }
        })

    key = ApiKey(g.account.id)
    key.save(True)

    return jsonify({
        'success': True,
        'key': key.serialize()
    })


@app.route('/api/<token>', methods=['DELETE'])
@authenticated
def api_key_delete(token):
    key = ApiKey.find_by_token(token)
    if not key:
        abort(404)

    key.disable()

    return jsonify({'success': True})
