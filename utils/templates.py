# -*- coding:utf-8 -*-

from jinja2 import evalcontextfilter, Markup
import cgi


@evalcontextfilter
def nl2br(eval_ctx, value):
    if not value:
        return value

    # We use cgi because jinja2.escape doesn't seems to work correctly in our case
    value = cgi.escape(value, True)
    value = value.replace('\r\n', '\n').replace('\r', '\n').replace('\n', '<br />')

    if eval_ctx.autoescape:
        value = Markup(value)

    return value


def dateformat(value, format='%d/%m/%Y'):
    if not value:
        return ''

    return value.strftime(format)


def timeformat(value, format='%H:%M:%S'):
    if not value:
        return ''

    return value.strftime(format)


def datetimeformat(value, format='%d/%m/%Y %H:%M'):
    if not value:
        return ''

    return value.strftime(format.encode('utf-8')).decode('utf-8')


def price(amount, currency=None, thousands=False):
    if currency is None:
        currency = '$'

    if isinstance(amount, str):
        try:
            amount = float(amount.replace(',', '.'))
        except Exception:
            return amount

    if not isinstance(amount, (int, float)):
        return amount

    result = "{:,.2f}".format(float(amount))
    if result[-2:-1] == '.':
        result = result + '0'

    if result[-3:] == '.00':
        result = result[0:-3]

    if thousands:
        if amount >= 1000:
            if result[-3:] == '000':
                result = '{0}k'.format(result[0:-3])
            elif result[-2:] == '00':
                result = '{0}k'.format(result[0:-2])

            if result.find(',k') > -1:
                result = result.replace(',k', 'k')

    if amount < 0:
        return '-{0}{1}'.format(currency, result[1:])
    else:
        return '{0}{1}'.format(currency, result)
