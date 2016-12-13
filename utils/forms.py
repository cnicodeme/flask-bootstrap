# -*- coding:utf-8 -*-

from wtforms import Form
from flask import jsonify, make_response


class BaseForm(Form):
    def errors_as_json(self, code=400):
        return make_response(jsonify(self.errors), code)

    def get_as_dict(self):
        results = {}
        for key in self._fields:
            if 'csrf_token' == key:
                continue

            value = getattr(self, key).data
            if value is None:
                continue

            results[key] = value

        return results
