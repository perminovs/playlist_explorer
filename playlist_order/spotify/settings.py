from pydantic import BaseSettings


class SpotifySettings(BaseSettings):
    api_host: str = 'https://api.spotify.com'

    user_info_path: str = 'v1/me'

    @property
    def user_info_url(self):
        return f'{self.api_host}/{self.user_info_path}'

    class Config:
        env_prefix = 'SPOTIFY_'
