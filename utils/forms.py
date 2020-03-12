# -*- coding:utf-8 -*-

from wtforms import Form
from flask import jsonify, make_response
from werkzeug.datastructures import CombinedMultiDict, ImmutableMultiDict
from werkzeug.exceptions import HTTPException
from wtforms import validators
from utils.countries import get_vat_details


class BaseForm(Form):
    def get_as_dict(self):
        results = {}
        for key in self._fields:
            if key == 'csrf_token':
                continue

            value = getattr(self, key).data
            if value is None:
                continue

            results[key] = value

        return results

    def error(self, key, message):
        self.errors[key] = [message]
        raise FormException(self.errors)

    def validate(self):
        super().validate()
        if len(self.errors) > 0:
            raise FormException(self.errors)

    @classmethod
    def load(cls, request, *args, **kwargs):
        if request.files:
            return cls(CombinedMultiDict((request.files, request.form)))
        elif request.get_json():
            return cls(ImmutableMultiDict(request.get_json()), *args, **kwargs)

        return cls(request.form, *args, **kwargs)


class FormException(HTTPException):
    def __init__(self, errors):
        self.errors = errors

    def get_response(self, environ=None):
        return make_response(jsonify({
            'success': False,
            'errors': self.errors
        }), 400)


class ValidateLength:
    def __init__(self, min=None, max=None, message=None):
        self.min = min
        self.max = max

    def __call__(self, form, field):
        if field.data is None:
            return None

        if self.min and len(field.data) < self.min:
            raise validators.ValidationError('Minimum length value of {0} allowed.'.format(self.min))

        if self.max and len(field.data) > self.max:
            raise validators.ValidationError('Maximum length value of {0} allowed.'.format(self.max))


class ValidateVat:
    def __init__(self, validate_country=True, validate_vies=True):
        self.validate_country = validate_country
        self.validate_vies = validate_vies

    def __call__(self, form, field):
        if field.data is None:
            # We don't care if it's required or not at this level
            return None

        if self.validate_country:
            if 'country' in form and form.country.data:
                if form.country.data != field.data[0:2]:
                    raise validators.ValidationError('')

        vat_number = field.data

        """
        @see https://www.iecomputersystems.com/ordering/eu_vat_numbers.htm
        @see https://en.wikipedia.org/wiki/VAT_identification_number
        @see http://ec.europa.eu/taxation_customs/vies/faqvies.do#item_11
        """

        vat_number = vat_number.upper().replace(' ', '').strip().replace('-', '').replace('.', '')

        country_code = vat_number[0:2].upper()
        if country_code == 'AT':  # Austria
            """ AT U 12345678 """
            try:
                assert vat_number[2:3] == 'U'
                assert len(vat_number) == 11
                int(vat_number[3:])
            except (AssertionError, ValueError):
                raise validators.ValidationError('Invalid VAT number. Must be ATU followed by 8 digits.')
        elif country_code == 'BE':  # Belgium
            """ BE 123456789 """
            try:
                assert len(vat_number) == 12
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be BE followed by 10 digits.')
        elif country_code == 'BG':  # Bulgaria
            """ BG 123456789 """
            try:
                assert len(vat_number) == 11 or len(vat_number) == 12
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be BG followed by 9 or 10 digits.')
        elif country_code == 'CY':  # Cyprus
            """ CY 12345678 X """
            try:
                assert len(vat_number) == 11
                int(vat_number[2:10])
                assert vat_number[10:].isalpha()
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be CY followed by 8 digits and a letter.')
        elif country_code == 'CZ':  # Czech Republic
            """ CZ 12345678(9)(10) """
            try:
                assert len(vat_number) >= 10
                assert len(vat_number) <= 12
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be CZ followed by 8, 9 or 10 digits.')
        elif country_code == 'DK':  # Denmark
            """ DK 12345678 """
            try:
                assert len(vat_number) == 10
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be DK followed by 8 digits.')
        elif country_code == 'EE':  # Estonia
            """ EE 123456789 """
            try:
                assert len(vat_number) == 11
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be EE followed by 9 digits.')
        elif country_code == 'FI':  # Finland
            """ FI 12345678 """
            try:
                assert len(vat_number) == 10
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be FI followed by 8 digits.')
        elif country_code == 'FR':  # France
            """ FR 12345678901 / FR X2345678901 / FR 1X345678901 / FR XX345678901 """

            try:
                assert len(vat_number) == 13
                if vat_number[2:3].isalpha():
                    assert vat_number[2:3] not in ('O', 'I')
                    int(vat_number[3:])
                elif vat_number[2:4].isalpha():
                    int(vat_number[4:])
                    assert vat_number[2:3] not in ('O', 'I')
                    assert vat_number[3:4] not in ('O', 'I')
                elif vat_number[3:4].isalpha():
                    assert vat_number[3:4] not in ('O', 'I')
                    int(vat_number[4:])
                    int(vat_number[2:3])
                else:
                    int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be FR followed by 11 digits or 1 letter and 10 digits or 2 letters and 9 digits.')
        elif country_code == 'DE':
            """ DE 123456789 """
            try:
                assert len(vat_number) == 11
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be DE followed by 9 digits.')
        elif country_code == 'EL':
            """ EL 012345678 """
            try:
                assert len(vat_number) == 11
                int(vat_number[2:])
                assert int(vat_number[2:3]) == 0
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be EL followed by 0 then 8 digits.')
        elif country_code == 'HU':
            """ HU 12345678 """
            try:
                assert len(vat_number) == 10
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be HU followed by 8 digits.')
        elif country_code == 'IE':
            """ IE 1234567X / IE 1X34567X """
            try:
                if len(vat_number) == 10:
                    int(vat_number[2:9])
                    assert vat_number[9:].isalpha()
                elif len(vat_number) == 11:
                    if vat_number[3:4].isalpha():
                        # Old format
                        int(vat_number[2:3])
                        assert vat_number[9:10].isalpha()
                        int(vat_number[4:9])
                    else:
                        int(vat_number[2:9])
                        assert vat_number[9:11].isalpha()
                else:
                    raise AssertionError('Invalid length')

                assert vat_number[9:].isalpha()
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be IE followed by 7 digits and 1/2 letters, or 1 digit, 1 letter and 5 digits then 1 letter.')
        elif country_code == 'IT':
            """ IT 12345678901 """
            try:
                assert len(vat_number) == 13
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be IT followed by 11 digits.')
        elif country_code == 'LV':
            """ LV 12345678901 """
            try:
                assert len(vat_number) == 13
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be LV followed by 11 digits.')
        elif country_code == 'LT':
            """ LT 123456789 / LT 123456789012 """
            try:
                assert len(vat_number) == 11 or len(vat_number) == 14
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be LT followed by 9 or 12 digits.')
        elif country_code == 'LU':
            """ LU 12345678 """
            try:
                assert len(vat_number) == 10
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be LU followed by 8 digits.')
        elif country_code == 'MT':
            """ MT 12345678 """
            try:
                assert len(vat_number) == 10
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be MT followed by 8 digits.')
        elif country_code == 'NL':
            """ NL 123456789B01 """
            try:
                assert len(vat_number) == 14
                assert vat_number[11:12] == 'B'
                int(vat_number[2:11])
                int(vat_number[12:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be NL followed by 9 digits, "B" and 2 digits.')
        elif country_code == 'PL':
            """ PL 1234567890 """
            try:
                assert len(vat_number) == 12
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be PL followed by 10 digits.')
        elif country_code == 'PT':
            """ PT 123456789 """
            try:
                assert len(vat_number) == 11
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be PT followed by 9 digits.')
        elif country_code == 'SK':
            """ SK 1234567890 """
            try:
                assert len(vat_number) == 12
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be SK followed by 10 digits.')
        elif country_code == 'SI':
            """ SI 12345678 """
            try:
                assert len(vat_number) == 10
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be SI followed by 8 digits.')
        elif country_code == 'ES':
            """ ES X12345678 / ES 12345678X / ES X1234567X """
            try:
                assert len(vat_number) == 11
                if vat_number[2:3].isalpha():
                    if vat_number[10:11].isalpha():
                        int(vat_number[3:10])
                    else:
                        int(vat_number[3:])
                else:
                    int(vat_number[2:10])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be ES followed by either 1 letter and 8 digits, 8 digits and 1 letter or 1 letter, 7 digits and 1 letter.')
        elif country_code == 'SE':
            """ SE 123456789001 """
            try:
                assert len(vat_number) == 14
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be SE followed by 12 digits.')
        elif country_code == 'GB':
            """ GB 123456789 / GB 123456789001 """
            try:
                assert len(vat_number) == 11 or len(vat_number) == 14 or len(vat_number) == 7
                if len(vat_number) != 7:
                    int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be GB followed by 9 or 12 digits or 5 characters.')
        elif country_code == 'RO':  # Romania
            """ RO 12345678 """
            try:
                assert len(vat_number) >= 4 and len(vat_number) <= 12
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be RO followed by at least 2 digits.')
        elif country_code == 'HR':  # Croatia
            """ HR 12345678999 """
            try:
                assert len(vat_number) == 13
                int(vat_number[2:])
            except (ValueError, AssertionError):
                raise validators.ValidationError('Invalid VAT number. Must be HR followed by 11 digits.')
        else:
            raise validators.ValidationError('Invalid country code.')

        if self.validate_vies:
            try:
                result = get_vat_details(vat_number)
                assert result['valid'] is True
            except ValueError as e:
                raise validators.ValidationError(str(e))
            except AssertionError:
                raise validators.ValidationError('Invalid VAT Number provided')


def encode_email(value):
    if value:
        try:
            mbox, domain = value.lower().split('@')
            domain = '.'.join([x.encode('idna').decode('utf-8') for x in domain.split('.')])
            return '{}@{}'.format(mbox, domain)
        except ValueError as e:  # Invalid split
            return None
        except UnicodeError as e:
            return None

    return None
