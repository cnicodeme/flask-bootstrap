# -*- coding:utf-8 -*-


class BaseForm(Form):
    def errors_as_json(self):
        return jsonify(self.errors), 400

    def get_as_dict(self):
        results = {}
        for key in self._fields:
            if 'csrf_token' == key: continue
            results[key] = getattr(self, key).data

        return results