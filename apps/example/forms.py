# -*- coding:utf-8 -*-

from utils.forms import BaseForm
from flask_wtf import Form
from wtforms import StringField, TextAreaField, IntegerField, validators, ValidationError

class ContactForm(BaseForm):
    display     = StringField("Your name", validators=[validators.DataRequired(),])
    email       = StringField("Your email", validators=[validators.DataRequired(),validators.Email()], filters = [lambda x: x or None])
    subject     = StringField("Subject", validators=[validators.DataRequired(),])
    message     = TextAreaField("Your message", filters = [lambda x: x or None], validators=[validators.DataRequired(),])
