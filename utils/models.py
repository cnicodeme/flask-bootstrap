# -*- config:utf-8 -*-
from flask_wtf import Form
from database import db

class ORModel(object):
    @classmethod
    def create(cls, form=None, **kwargs):
        if form:
            if not isinstance(form, Form):
                raise Exception("Given form \"{0}\" in Model must be an instance of wtforms.Form".format(form.__class__.__name__))

            kwargs = form.get_as_dict()

        instance = cls(**kwargs)
        return instance

    def update(self, form=None, **kwargs):
        if form:
            if not isinstance(form, Form):
                raise Exception("Given form \"{0}\" in Model must be an instance of wtforms.Form".format(form.__class__.__name__))

            kwargs = form.get_as_dict()

        for attr, value in kwargs.iteritems():
            setattr(self, attr, value)

        return self

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        return commit and db.session.commit()

import sqlalchemy.types as types

class DbAmount(types.TypeDecorator):
    impl = types.Integer

    def load_dialect_impl(self, dialect):
        return dialect.type_descriptor(types.Integer)


    def process_bind_param(self, value, dialect):
        if not value:
            return None

        return float(value) * 100


    def process_result_value(self, value, dialect):
        if not value:
            return 0

        result = "{0:.2f}".format(float(value)/100)
        if result[-3:] == '.00':
            return result[0:-3]

        return result
