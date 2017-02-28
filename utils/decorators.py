# coding=utf-8

from functools import wraps
from flask import session, abort


def authenticated(view_func):
    def _decorator(*args, **kwargs):
        if not 'email' in session:
            return abort(403)

        """
        from account.models import Account

        account = Account.find_by_email(session['email'])

        if not account:
            return redirect(url_for('auth.login'))

        g.account = account
        """
        return view_func(*args, **kwargs)

    return wraps(view_func)(_decorator)
