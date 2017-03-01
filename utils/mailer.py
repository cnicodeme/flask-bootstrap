# -*- coding:utf-8 -*-

from flask import current_app
import mimetypes, requests, os

mimetypes.init()


def guess_mimetype(name):
    type_found = mimetypes.guess_type(name)
    if type_found:
        return type_found[0]  # Best guess

    return 'text/plain'


class EmailMessage(object):
    def __init__(self, subject, template=None, text=None, html=None):
        self.data = {
            'options': {
                'open_tracking': True,
                'click_tracking': True,
                'transactional': False,
                'inline_css': True
            },
            'recipients': [],
            'content': {
                'subject': subject,
                'attachments': [],
                'inline_images': [],
                'text': None,
                'html': None,
            }
        }

        self.set_from(current_app.config['CONTACT_NAME'], current_app.config['CONTACT_EMAIL'])

        if template:
            # set html and text
            path = os.path.join(current_app.root_path, current_app.template_folder, 'emails')

            try:
                txt_file = open(os.path.join(path, '{0}.txt'.format(template)))
                self.data['content']['text'] = txt_file.read()
                txt_file.close()
            except IOError:
                pass

            try:
                html_file = open(os.path.join(path, '{0}.html'.format(template)))
                self.data['content']['html'] = html_file.read()
                html_file.close()
            except IOError:
                pass

        if text:
            self.data['content']['text'] = text

        if html:
            self.data['content']['html'] = html

        if not self.data['content']['text'] and not self.data['content']['html']:
            raise ValueError('Unable to find the specified template.')

    def set_from(self, from_name, from_email):
        self.data['content']['from'] = {
            'name': from_name,
            'email': from_email
        }

        self.data['content']['reply-to'] = from_email

    def _add(self, kind, name, content, type=None):
        if not type:
            type = guess_mimetype(name)

        self.data['content'][kind].append({
            'type': type,
            'name': name,
            'data': content.encode('base64')
        })

    def add_attachment(self, name, content, type=None):
        self._add('attachments', name, content, type)

    def add_inline(self, name, content, type=None):
        self._add('inline_images', name, content, type)

    def queue(self, name, email, substitution=None):
        self.data['recipients'].append({
            'address': {
                'name': name,
                'email': email
            },
            'substitution_data': substitution
        })

    def send_to(self, name, email, substitution=None, send_at=None):
        self.data['recipients'] = []
        self.queue(name, email, substitution)
        return self.send(send_at)

    # TODO Manage sending limit
    def send(self, send_at=None):
        if current_app.config.get('SPARKPOST_KEY', None) is None:
            raise Exception('Missing SPARKPOST_KEY config value.')

        if send_at:
            self.data['options']['start_time'] = send_at.replace(microsecond=0).isoformat()

        try:
            requests.packages.urllib3.disable_warnings()
            r = requests.post(
                'https://api.sparkpost.com/api/v1/transmissions',
                verify=False,
                timeout=10,
                headers={'Authorization': current_app.config['SPARKPOST_KEY']},
                json=self.data
            )

            if r.status_code == 200:
                response = r.json()
                return response['results']['id']
        except requests.exceptions.RequestException:
            current_app.logger.exception('[SparkPost]')

        return None
