from __future__ import annotations

import json
import pathlib
import webbrowser
from datetime import datetime
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Optional

from pydantic import BaseModel

from auth.settings import BaseAuthSettings


class AuthCodeGetter:
    def __init__(self, settings: BaseAuthSettings):
        self._settings = settings

    @property
    def code(self):
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


class Token(BaseModel):
    value: str
    expire_time: datetime

    @property
    def is_expire(self):
        return self.expire_time < datetime.now()

    def dump(self, path: pathlib.Path) -> None:
        with path.open('w') as f:
            json.dump(self.json(), f)

    @classmethod
    def load(cls, path: pathlib.Path) -> Optional[Token]:
        if not path.exists():
            return None
        with path.open() as f:
            try:
                return cls(**json.loads(json.load(f)))
            except Exception:
                return None
