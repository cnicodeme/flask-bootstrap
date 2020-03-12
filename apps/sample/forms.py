# -*- coding:utf-8 -*-

from utils.forms import BaseForm, ValidateLength, encode_email
from wtforms import StringField, validators


class SampleForm(BaseForm):
    email           = StringField(validators=[validators.DataRequired(), validators.Email(), ValidateLength(max=250)], filters=[encode_email])
