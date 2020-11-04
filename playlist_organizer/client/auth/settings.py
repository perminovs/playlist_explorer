import abc
from urllib.parse import urlencode

from pydantic import BaseSettings


class BaseAuthSettings(BaseSettings, abc.ABC):
    app_id: str
    secret_key: str
    permissions: str

    redirect_port: int
    redirect_host: str

    service_host: str
    code_path: str
    token_path: str

    @property
    @abc.abstractmethod
    def code_url(self) -> str:
        pass

    @property
    def token_url(self) -> str:
        return f'{self.service_host}/{self.token_path}'


class DeezerAuthSettings(BaseAuthSettings):
    redirect_port: int = 8912
    redirect_host: str = 'http://localhost'

    permissions: str = 'basic_access,email,manage_library'

    service_host: str = 'https://connect.deezer.com'
    code_path: str = 'oauth/auth.php'
    token_path: str = 'oauth/access_token.php'

    @property
    def code_url(self) -> str:
        _params = urlencode(
            {
                'app_id': self.app_id,
                'redirect_uri': f'{self.redirect_host}:{self.redirect_port}',
                'perms': self.permissions,
            }
        )
        return f'{self.service_host}/{self.code_path}?{_params}'

    class Config:
        env_prefix = 'DEEZER_AUTH_'


class SpotifyAuthSettings(BaseAuthSettings):
    redirect_port: int = 8000
    redirect_host: str = 'http://localhost'

    permissions: str = (
        'user-read-private user-read-email playlist-read-private playlist-read-collaborative '
        'playlist-modify-private playlist-modify-public'
    )

    service_host: str = 'https://accounts.spotify.com'
    code_path: str = 'authorize'
    token_path: str = 'api/token'

    @property
    def code_url(self) -> str:
        _params = urlencode(
            {
                'response_type': 'code',
                'client_id': self.app_id,
                'scope': self.permissions,
                'redirect_uri': f'{self.redirect_host}:{self.redirect_port}',
            }
        )
        return f'https://accounts.spotify.com/authorize?{_params}'

    class Config:
        env_prefix = 'SPOTIFY_AUTH_'
