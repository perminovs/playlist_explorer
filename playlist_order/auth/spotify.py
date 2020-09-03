from __future__ import annotations

import logging
import pathlib
from base64 import b64encode
from datetime import datetime, timedelta
from typing import Optional

import httpx

from auth.base import AuthCodeGetter, Token
from auth.settings import SpotifyAuthSettings

logger = logging.getLogger(__name__)
_TOKEN_PATH = pathlib.Path(__file__).parent / '.spotify-token.dump'


class SpotifyAuthenticator:
    def __init__(self, auth_code_getter: AuthCodeGetter, settings: SpotifyAuthSettings):
        self._settings = settings
        self._auth_code_getter = auth_code_getter

        self._token: Optional[Token] = None

    @property
    def _is_token_valid(self):
        return self._token and not self._token.is_expire

    @property
    def token(self) -> str:
        if self._is_token_valid:
            return self._token.value

        logger.debug('No valid token in memory found')
        token = Token.load(_TOKEN_PATH)
        if token:
            self._token = token

        if self._is_token_valid:
            logger.debug('Dumped token found')
            return self._token.value

        logger.debug('No valid token in file found, get new one from spotify')

        _auth = b64encode((self._settings.app_id + ':' + self._settings.secret_key).encode()).decode()
        headers = {'Authorization': f'Basic {_auth}'}
        payload = {
            'code': self._auth_code_getter.code,
            'redirect_uri': f'{self._settings.redirect_host}:{self._settings.redirect_port}',
            'grant_type': 'authorization_code'
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

        self._token = Token(value=token_, expire_time=datetime.now() + timedelta(seconds_left))
        self._token.dump(_TOKEN_PATH)
        return self._token.value
