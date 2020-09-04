from __future__ import annotations

import logging
from base64 import b64encode
from datetime import datetime, timedelta

import httpx

from playlist_order.auth.base import BaseAuthenticator, Token

logger = logging.getLogger(__name__)


class SpotifyAuthenticator(BaseAuthenticator):
    def _get_token(self) -> Token:
        creds = self._settings.app_id + ':' + self._settings.secret_key
        _auth = b64encode(creds.encode()).decode()
        headers = {'Authorization': f'Basic {_auth}'}
        payload = {
            'code': self._code,
            'redirect_uri': f'{self._settings.redirect_host}:{self._settings.redirect_port}',
            'grant_type': 'authorization_code',
        }
        resp = httpx.post(self._settings.token_url, data=payload, headers=headers)
        resp.raise_for_status()
        json_data = resp.json()
        try:
            token_ = json_data['access_token']
            seconds_left = json_data['expires_in']
        except KeyError:
            logger.warning('Unknown spotify response\n%s', json_data)
            raise

        token = Token(value=token_, expire_time=datetime.now() + timedelta(seconds_left))
        logger.info('Got token, expires at %s after %s sec', token.expire_time, seconds_left)
        return token
