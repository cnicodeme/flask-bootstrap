# -*- config:utf-8 -*-

from utils.forms import BaseForm
from database import db
import sqlalchemy.types as types
import datetime


class ORModel(object):
    @classmethod
    def create(cls, form=None, **kwargs):
        if form:
            if not isinstance(form, BaseForm):
                raise Exception("Given form \"{0}\" in Model must be an instance of utils.forms.BaseForm".format(form.__class__.__name__))

            kwargs = form.get_as_dict()

        instance = cls()
        for key in kwargs:
            method = getattr(instance, 'set_{0}'.format(key), None)
            if method and callable(method):
                method(kwargs[key])
            else:
                setattr(instance, key, kwargs[key])

        return instance

    def update(self, form=None, **kwargs):
        if form:
            if not isinstance(form, BaseForm):
                raise Exception("Given form \"{0}\" in Model must be an instance of utils.forms.BaseForm".format(form.__class__.__name__))

            kwargs = form.get_as_dict()

        for attr, value in kwargs.items():
            method = getattr(self, 'set_{0}'.format(attr), None)
            if method and callable(method):
                method(value)
            else:
                setattr(self, attr, value)

        return self

    def save(self, commit=True):
        db.session.add(self)
        if commit:
            db.session.commit()
        return self

    def delete(self, commit=True):
        db.session.delete(self)
        if commit:
            return db.session.commit()

        return True


class JsonSerializable(object):
    __jsonserialize__ = ['id', ('__str__', 'display')]
    UNIX_EPOCH = datetime.datetime(1970, 1, 1, 0, 0)

    def simple_serializer(self, item):
        if hasattr(item, 'serialize'):
            return getattr(item, 'serialize')()

        return {'id': item.id, 'display': item.__str__()}

    def serialize(self, columns=None):
        if not columns:
            if hasattr(self.__jsonserialize__, '__call__'):
                return self.__jsonserialize__()

            columns = self.__jsonserialize__

        json = {}

        for column in columns:
            key = column

            if isinstance(column, tuple):
                key = column[1]
                column = column[0]

            prop = None
            if column.find('.') != -1:
                parts = column.split('.')
                prop = self
                for part in parts:
                    if not prop:
                        break
                    prop = getattr(prop, part, None)
            else:
                prop = getattr(self, column, None)

            if hasattr(prop, '__call__'):
                # In case we want to serialize a method
                if key[0:4] == 'get_':
                    key = key[4:]

                json[key] = prop()
            elif isinstance(prop, JsonSerializable):
                json[key] = prop.serialize()
            elif isinstance(prop, db.Model):
                # if a model, we simple serialize it
                json[key] = self.simple_serializer(prop)

            elif isinstance(prop, list):
                # Can be a list of direct item, or a list from a m2m
                # If it's a direct item, we go for it
                # If it's a m2m, we get the details of the related object
                json[key] = []
                for item in prop:
                    if isinstance(item, JsonSerializable):
                        json[key].append(self.serialize(item))
                    else:
                        json[key].append(self.simple_serializer(item))

            elif isinstance(prop, datetime.datetime):
                # In case of a date, we output a timestamp
                json[key] = int((prop - self.UNIX_EPOCH).total_seconds() * 1000)
            elif isinstance(prop, datetime.date):
                # In case of a date, we output a timestamp
                json[key] = int((datetime.datetime.combine(prop, datetime.datetime.min.time()) - self.UNIX_EPOCH).total_seconds() * 1000)
            else:
                json[key] = prop

        return json

    def _map_object(json, key, value):
        if key.find('.') == -1:
            json[key] = value
        else:
            parts = key.split('.')
            current = json
            for part in parts:
                if not current[part]:
                    current[part] = {}


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

        result = "{0:.2f}".format(float(value) / 100)
        if result[-3:] == '.00':
            return result[0:-3]

        return result
