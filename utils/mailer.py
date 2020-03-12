# -*- coding:utf-8 -*-

from flask import current_app, render_template_string
import mimetypes, requests, os, json

mimetypes.init()


def guess_mimetype(name):
    type_found = mimetypes.guess_type(name)
    if type_found:
        return type_found[0]  # Best guess

    return 'text/plain'


class Mailgun(object):
    def __init__(self, subject, template=None, text=None, html=None):
        self.files = {}
        self.data = {
            'from': None,
            'to': [],
            'cc': [],
            'bcc': [],
            'subject': subject,
            'text': None,
            'html': None,
            'o:tag': None,
            'o:campaign': None,
            'o:deliverytime': None,
            'o:tracking': 'yes',
            'o:tracking-clicks': 'htmlonly',
            'o:tracking-opens': 'yes',
            'h:X-Version': '{} v1'.format(current_app.config.get('APPLICATION_NAME'))
        }

        self.set_from(current_app.config['CONTACT_NAME'], current_app.config['CONTACT_EMAIL'])

        if template:
            # set html and text
            path = os.path.join(current_app.root_path, current_app.template_folder, 'emails')

            try:
                txt_file = open(os.path.join(path, '{0}.txt'.format(template)))
                self.data['text'] = txt_file.read()
                txt_file.close()
            except IOError:
                self.data['text'] = None

            try:
                html_file = open(os.path.join(path, '{0}.html'.format(template)))
                self.data['html'] = html_file.read()
                html_file.close()
            except IOError:
                self.data['html'] = None

        if text:
            self.data['text'] = text

        if html:
            self.data['html'] = html

        if not self.data['text'] and not self.data['html']:
            raise ValueError('Unable to find the specified template.')

    def _set_email(self, name, email):
        if name is None:
            return email

        name = name.replace('<', '').replace('>', '').replace('@', '').replace('"', '').replace("'", '')
        return '{0} <{1}>'.format(name, email)

    def set_from(self, from_name, from_email):
        self.data['from'] = self._set_email(from_name, from_email)

    def set_reply_to(self, from_name, from_email):
        self.data['h:Reply-To'] = self._set_email(from_name, from_email)

    def add_attachment(self, name, content, type=None):
        """
        Add attachment with content as binary content of the opened file
        """
        if not type:
            type = guess_mimetype(name)

        #           attachment[0]
        self.files['attachment[' + str(len(self.files)) + ']'] = (name, content, type)

    def send(self, account, substitution=None, send_at=None):
        if not substitution:
            substitution = {}

        if 'name' not in substitution:
            substitution['name'] = str(account)

        if 'firstname' not in substitution and hasattr(account, 'get_firstname'):
            substitution['firstname'] = account.get_firstname()

        return self.send_to(
            str(account),
            account.email,
            substitution=substitution,
            send_at=send_at
        )

    def send_to(self, name, email, substitution=None, send_at=None):
        self.data['to'] = []
        self.data['cc'] = []
        self.data['bcc'] = []

        self.data['to'].append(self._set_email(name, email))

        if substitution is None:
            substitution = {}

        if substitution:
            self.data['subject'] = render_template_string(self.data['subject'], **substitution)
            substitution['subject'] = self.data['subject']

            if self.data['text'] is not None:
                self.data['text'] = render_template_string(self.data['text'], **substitution)

            if self.data['html'] is not None:
                self.data['html'] = render_template_string(self.data['html'], **substitution)

        self._send(send_at)

    def _send(self, send_at=None):
        # We do some changes to data so we make a copy of it
        if send_at:
            # @see http://stackoverflow.com/questions/3453177/convert-python-datetime-to-rfc-2822
            # Thu, 13 Oct 2011 18:02:00 GMT
            self.data['o:deliverytime'] = send_at.strftime('%a, %d %b %Y %H:%M:%S') + ' GMT'

        debug_mode = False
        if current_app.config.get('MAILGUN_API_KEY', None) is None:
            debug_mode = True

        if current_app.debug:
            debug_mode = True

        if debug_mode:
            current_app.logger.info('MOCK MAILER')
            current_app.logger.info(json.dumps(self.data, indent=4))
        else:
            requests.packages.urllib3.disable_warnings()
            r = None
            try:
                r = requests.post(
                    "{0}/messages".format(current_app.config['MAILGUN_API_URL']),
                    auth=('api', current_app.config['MAILGUN_API_KEY']),
                    data=self.data,
                    files=self.files,
                    verify=False,
                    timeout=20
                )
                r.raise_for_status()
                return r.json()
            except requests.exceptions.RequestException:
                pass

        return None
