'''
nexmo.sms - Nexmo SMS API interface.
'''

import requests

from .auth import requires_auth, SecretBodyAuth, SignatureAuth
from .exceptions import AuthenticationError, ClientError, ServerError


class SMSProvider(object):
    def __init__(self, config):
        self.config = config
        self.base = 'https://rest.nexmo.com'
        self.session = requests.Session()
        self.session.headers.update({'user-agent': ''})

    @requires_auth([SignatureAuth, SecretBodyAuth])
    def send_text(
            self,
            *,
            from_,
            to,
            text,
            unicode_=False,
            status_report_req=False,
            callback=None,
            message_class=None,
            _auth=None,  # auth is provided by `requires_auth`
            **kwargs):
        """
        Send an SMS text or unicode message.

        :param str from_:
        :param str to:
        :param str text:
        :param bool unicode_:
        :param bool status_report_req:
        :param str callback:
        :param int message_class:
        :return:
        """

        # Construct params dict:
        params = {
            'from': from_,
            'to': to,
            'text': text,
            'type': 'text' if not unicode_ else 'unicode',
        }

        if status_report_req or callback is not None:
            params['status-report-req'] = 1

        if callback is not None:
            params['callback'] = callback

        if message_class is not None:
            params['message-class'] = message_class

        # Generate request:
        uri = self.base + '/sms/json'
        request = requests.Request("POST", uri, data=params)
        _auth(request, **kwargs)

        response = self.session.send(request.prepare())
        return parse_response(response)


def parse_response(response, response_type=None):
    if response.status_code == 401:
        raise AuthenticationError()
    elif response.status_code == 204:
        return None
    elif 200 <= response.status_code < 300:
        json = response.json()
        if response_type is None:
            return json
        else:
            # TODO: Handle object mapping here:
            return json
    elif 400 <= response.status_code < 500:
        message = "{code} response from server".format(
            code=response.status_code)
        raise ClientError(message)
    elif 500 <= response.status_code < 600:
        message = "{code} response from server".format(
            code=response.status_code)
        raise ServerError(message)