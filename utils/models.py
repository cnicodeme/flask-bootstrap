# -*- config:utf-8 -*-


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