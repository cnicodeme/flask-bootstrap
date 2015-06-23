# -*- coding:utf-8 -*-
<<<<<<< HEAD
from flask_wtf import Form
=======

from flask_wtf import Form
from flask import jsonify
>>>>>>> 6df81820bf82c9b1045d3b66b4a1cac83dce560e

class BaseForm(Form):
    def errors_as_json(self):
        return jsonify(self.errors), 400

    def get_as_dict(self):
        results = {}
        for key in self._fields:
            if 'csrf_token' == key: continue
            results[key] = getattr(self, key).data

        return results
