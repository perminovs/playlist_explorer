from __future__ import annotations

import logging
from datetime import datetime, timedelta
from typing import Tuple

import httpx
from httpx import Response

from playlist_organizer.client.auth.base import BaseAuthenticator, Token

logger = logging.getLogger(__name__)


class DeezerAuthenticator(BaseAuthenticator):
    def _get_token(self) -> Token:
        params = {
            'app_id': self._settings.app_id,
            'secret': self._settings.secret_key,
            'code': self._code,
        }
        resp = httpx.post(self._settings.token_url, data=params)
        resp.raise_for_status()

        try:
            value, seconds_left = _parse_deezer_response(resp)
        except Exception:
            logger.warning('Unknown deezer response\n%s', resp.text)
            raise

        token = Token(value=value, expire_time=datetime.now() + timedelta(seconds=seconds_left))
        logger.info('Got token, expires at %s after %s sec', token.expire_time, seconds_left)
        return token


def _parse_deezer_response(response: Response) -> Tuple[str, int]:
    resp_text = response.text
    resp_text = resp_text.replace('access_token=', '')
    idx = resp_text.rfind('&expires=')
    token = resp_text[:idx]
    seconds_left = int(resp_text[idx + len('&expires=') :])
    return token, seconds_left
