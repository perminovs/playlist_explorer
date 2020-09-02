from urllib.parse import urlencode

from pydantic import BaseSettings


class DeezerSettings(BaseSettings):
    app_id: int
    app_name: str
    secret_key: str
    permitions: str

    redirect_port: int = 8912
    redirect_host: str = 'http://localhost'

    connect_host: str = 'https://connect.deezer.com'
    code_path: str = 'oauth/auth.php'
    token_path: str = 'oauth/access_token.php'

    api_host: str = 'https://api.deezer.com'

    user_info_path: str = 'user/me'
    playlists_path: str = 'playlists'
    playlist_info_path: str = 'playlist/{}'

    @property
    def code_url(self):
        _params = urlencode({
            'app_id': self.app_id,
            'redirect_uri': f'{self.redirect_host}:{self.redirect_port}',
            'perms': self.permitions,
        })
        return f'{self.connect_host}/{self.code_path}?{_params}'

    @property
    def token_url(self):
        return f'{self.connect_host}/{self.token_path}'

    @property
    def user_info_url(self):
        return f'{self.api_host}/{self.user_info_path}'

    @property
    def playlists_url(self):
        return f'{self.user_info_url}/{self.playlists_path}'

    @property
    def playlists_info_url(self):
        return f'{self.api_host}/{self.playlist_info_path}'

    class Config:
        env_prefix = 'DEEZER_'
