from __future__ import annotations

import logging
import pathlib
from datetime import datetime, timedelta
from typing import Tuple

import httpx
from httpx import Response

from auth.base import Token, BaseAuthenticator

logger = logging.getLogger(__name__)
_TOKEN_PATH = pathlib.Path(__file__).parent / '.deezer-token.dump'


class DeezerAuthenticator(BaseAuthenticator):
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

        logger.debug('No valid token in file found, get new one from deezer')

        params = {
            'app_id': self._settings.app_id,
            'secret': self._settings.secret_key,
            'code': self._code,
        }
        resp = httpx.post(self._settings.token_url, data=params)
        resp.raise_for_status()

        try:
            token, seconds_left = _parse_deezer_response(resp)
        except Exception:
            raise

        self._token = Token(value=token, expire_time=datetime.now() + timedelta(seconds=seconds_left))
        logger.info(f'Got token, expires at {self._token.expire_time} after %s sec', seconds_left)
        self._token.dump(_TOKEN_PATH)
        return self._token.value


def _parse_deezer_response(response: Response) -> Tuple[str, int]:
    resp_text = response.text
    resp_text = resp_text.replace('access_token=', '')
    idx = resp_text.rfind('&expires=')
    token = resp_text[:idx]
    seconds_left = int(resp_text[idx + len('&expires='):])
    return token, seconds_left
