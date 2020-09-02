from __future__ import annotations

import json
import pathlib
import webbrowser
from datetime import datetime, timedelta
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Tuple, Optional

import httpx
from httpx import Response
from pydantic import BaseModel

from deezer.settings import DeezerSettings
from deezer.utils import pprint_resp

_TOKEN_PATH = pathlib.Path(__file__).parent / '.token.dump'


class Token(BaseModel):
    value: str
    expire_time: datetime

    @property
    def is_expire(self):
        return self.expire_time < datetime.now()

    def dump(self) -> None:
        with _TOKEN_PATH.open('w') as f:
            json.dump(self.json(), f)

    @classmethod
    def load(cls) -> Optional[Token]:
        if not _TOKEN_PATH.exists():
            return None
        with _TOKEN_PATH.open() as f:
            try:
                return cls(**json.loads(json.load(f)))
            except Exception:
                return None


class DeezerAuthenticator:
    def __init__(self, settings: DeezerSettings):
        self._settings = settings

        self._token: Optional[Token] = None

    @property
    def _is_token_valid(self):
        return self._token and not self._token.is_expire

    @property
    def token(self):
        if self._is_token_valid:
            return self._token

        token = Token.load()
        if token:
            self._token = token

        if self._is_token_valid:
            return self._token

        print('Get new token')

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
            print(resp.text)
            raise

        print(f'{seconds_left = }')
        self._token = Token(value=token, expire_time=datetime.now() + timedelta(seconds=seconds_left))
        print(f'Got token, expires at {self._token.expire_time}')
        self._token.dump()
        return self._token

    def user_info(self):
        resp = httpx.get(
            self._settings.user_info_url,
            params={'access_token': self.token},
        )
        resp.raise_for_status()

        info = resp.json()
        pprint_resp(info)
        if any(key not in info for key in ('id', 'email', 'type')):
            raise ValueError(f'Token is not valid, got json:\n{info}')

    @property
    def _code(self):
        code = None

        class HttpHandler(BaseHTTPRequestHandler):
            def do_GET(handler):
                nonlocal code
                code = handler.path.replace('/?code=', '')

                handler.send_response(200)
                handler.send_header('Content-type', 'text/html')
                handler.end_headers()

        server_address = ('', self._settings.redirect_port)
        httpd = HTTPServer(server_address, HttpHandler)

        webbrowser.open(self._settings.code_url, new=2)
        httpd.handle_request()

        return code


def _parse_deezer_response(response: Response) -> Tuple[str, int]:
    resp_text = response.text
    resp_text = resp_text.replace('access_token=', '')
    idx = resp_text.rfind('&expires=')
    token = resp_text[:idx]
    seconds_left = int(resp_text[idx + len('&expires='):])
    return token, seconds_left
