# -*- coding:utf-8 -*-

from flask import request
from utils.forms import BaseForm, ValidateLength, ValidateVat, encode_email
from wtforms import StringField, validators
import requests


class AccountForm(BaseForm):
    email           = StringField(validators=[validators.DataRequired(), validators.Email(), ValidateLength(max=250)], filters=[encode_email])
    company_name    = StringField(validators=[validators.Optional(), ValidateLength(max=250)], filters=[lambda x: x or None])
    company_details = StringField(validators=[validators.Optional(), ValidateLength(max=250)], filters=[lambda x: x or None])
    company_vat     = StringField(validators=[validators.Optional(), ValidateLength(max=250), ValidateVat()], filters=[lambda x: x or None])
    country         = StringField(validators=[validators.Optional(), ValidateLength(2, 2)], filters=[lambda x: x or None])

    def validate_email(self, field):
        if not field.data:
            return None

    def validate_country(self, field):
        if not field.data:
            remote_addr = request.remote_addr
            if request.headers.getlist("X-Forwarded-For"):
                remote_addr = request.headers.getlist("X-Forwarded-For")[0]

            try:
                response = requests.get('http://ip-api.com/json/{0}?fields=countryCode'.format(remote_addr))
                response.raise_for_status()
                field.data = response.json().get('countryCode')
            except Exception:
                pass

        # Test if domain part is MX valid
        # Test if email is risky


class AccountUpdateForm(BaseForm):
    email           = StringField(validators=[validators.Optional(), validators.Email(), ValidateLength(max=250)], filters=[lambda x: x or None, encode_email])
    company_name    = StringField(validators=[validators.Optional(), ValidateLength(max=250)], filters=[lambda x: x or None])
    company_details = StringField(validators=[validators.Optional(), ValidateLength(max=250)], filters=[lambda x: x or None])
    company_vat     = StringField(validators=[validators.Optional(), ValidateLength(max=250), ValidateVat()], filters=[lambda x: x or None])
    country         = StringField(validators=[validators.Optional(), ValidateLength(2, 2)], filters=[lambda x: x or None])

    def validate_email(self, field):
        if not field.data:
            return None

        # Test if domain part is MX valid
        # Test if email is risky


class CompanyVatForm(BaseForm):
    company_vat     = StringField(validators=[validators.DataRequired(), ValidateLength(max=250), ValidateVat(validate_vies=False)])


class AccountPasswordForm(BaseForm):
    current  = StringField(validators=[validators.DataRequired(), ValidateLength(min=6, max=250)])
    password = StringField(validators=[validators.DataRequired(), ValidateLength(min=6, max=250)])
    confirm  = StringField(validators=[validators.DataRequired(), ValidateLength(min=6, max=250), validators.EqualTo('password', 'The passwords are not matching. Please check again.')])
