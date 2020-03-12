# -*- coding:utf-8 -*-

from flask import current_app
import requests, hashlib, json, socket


def amplitude_track(event_type, properties=None):
    if current_app.config.get('AMPLITUDE_API_KEY') is None:
        current_app.logger.error('AMPLITUDE API KEY not defined')
        return None

    message = {
        'device_id': hashlib.md5(socket.gethostbyname().encode()).hexdigest(),
        'event_type': event_type
    }

    if properties:
        message['event_properties'] = properties

    try:
        response = requests.post(
            'https://api.amplitude.com/httpapi',
            data={
                'api_key': current_app.config.get('AMPLITUDE_API_KEY'),
                'event': json.dumps(message)
            },
            timeout=3
        )
        response.raise_for_status()
    except Exception:
        current_app.logger.debug("[Amplitude]")


def twilio(to, message):
    if current_app.debug:
        current_app.logger.warning('No SMS sent in debug mode.')
        return None

    if current_app.config.get('TWILIO_AUTH_KEY', None) is None:
        if not current_app.debug:
            current_app.logger.warning('No TWILIO API Key found!')
        return None

    params = {
        'From': current_app.config.get('TWILIO_FROM'),
        'To': to,
        'Body': message
    }

    try:
        r = requests.post(
            'https://api.twilio.com/2010-04-01/Accounts/{0}/Messages.json'.format(current_app.config.get('TWILIO_AUTH_KEY')),
            auth=(current_app.config.get('TWILIO_AUTH_KEY'), current_app.config.get('TWILIO_AUTH_TOKEN')),
            data=params
        )

        r.raise_for_status()
    except Exception:
        current_app.logger.exception('[Twilio]')

    return None
