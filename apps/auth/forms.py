# -*- coding:utf-8 -*-

from utils.forms import BaseForm, ValidateLength, encode_email
from wtforms import StringField, PasswordField, validators


class AuthForm(BaseForm):
    email    = StringField(validators=[validators.DataRequired(), validators.Email(), ValidateLength(max=250)], filters=[encode_email])
    password = PasswordField(validators=[validators.Optional(), ValidateLength(6, 250)], filters=[lambda x: x or None])


class LostPasswordForm(BaseForm):
    email    = StringField(validators=[validators.DataRequired(), validators.Email(), ValidateLength(max=250)], filters=[encode_email])
