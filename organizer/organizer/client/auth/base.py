from __future__ import annotations

import abc
import json
import logging
import pathlib
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from json import JSONDecodeError
from typing import Optional

from pydantic import BaseModel

from organizer.client.auth.settings import BaseAuthSettings

logger = logging.getLogger(__name__)
_TOKEN_DIR = pathlib.Path(__file__).parent


class Token(BaseModel):
    value: str
    expire_time: datetime

    @property
    def is_expire(self) -> bool:
        return self.expire_time < datetime.now()

    def dump(self, path: pathlib.Path) -> None:
        with path.open('w') as f:
            json.dump(self.json(), f, ensure_ascii=False, indent=4, sort_keys=True)

    @classmethod
    def load(cls, path: pathlib.Path) -> Optional[Token]:
        if not path.exists():
            return None
        with path.open() as f:
            try:
                return cls(**json.loads(json.load(f)))
            except JSONDecodeError:
                return None


class BaseAuthenticator(abc.ABC):
    def __init__(self, settings: BaseAuthSettings) -> None:
        self._settings = settings
        self._token: Optional[Token] = None
        self._token_path = _TOKEN_DIR / f'{type(self).__name__}-token.dump'

    @property
    def token(self) -> str:
        if self._is_token_valid:
            return self._token.value  # type: ignore

        logger.debug('No valid token in memory found')
        token = Token.load(self._token_path)
        if token:
            self._token = token

        if self._is_token_valid:
            logger.debug('Dumped token found')
            return self._token.value  # type: ignore

        logger.debug('No valid token in file found, get new one')

        self._token = self._get_token()

        self._token.dump(self._token_path)
        return self._token.value

    @abc.abstractmethod
    def _get_token(self) -> Token:
        pass

    @property
    def _is_token_valid(self) -> bool:
        return bool(self._token and not self._token.is_expire)

    @property
    def _code(self) -> str:
        code = None

        class HttpHandler(BaseHTTPRequestHandler):
            def do_GET(handler) -> None:  # noqa N805, N802
                nonlocal code
                code = handler.path.replace('/?code=', '')
                response_body = '<h3>dude, u can close the tab now and return to terminal</h3>'

                handler.send_response(200)
                handler.send_header("Content-Type", "text/html")
                handler.send_header("Content-Length", str(len(response_body)))
                handler.end_headers()
                handler.wfile.write(response_body.encode())

        server_address = ('', self._settings.redirect_port)
        httpd = HTTPServer(server_address, HttpHandler)

        code_url = self._settings.code_url
        logger.debug('Open %s', code_url)
        webbrowser.open(code_url, new=2)
        httpd.handle_request()

        if code is None:
            raise RuntimeError('Auth failed, something went wrong')
        return code
