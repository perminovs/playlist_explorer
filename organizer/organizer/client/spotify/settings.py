from pydantic import BaseSettings


class SpotifySettings(BaseSettings):
    api_host: str = 'https://api.spotify.com'

    user_info_path: str = 'v1/me'
    playlists_path: str = 'v1/me/playlists'
    playlist_info_path: str = 'v1/playlists/{}/tracks'

    @property
    def user_info_url(self) -> str:
        return f'{self.api_host}/{self.user_info_path}'

    @property
    def playlists_url(self) -> str:
        return f'{self.api_host}/{self.playlists_path}'

    @property
    def playlists_info_url(self) -> str:
        return f'{self.api_host}/{self.playlist_info_path}'

    class Config:
        env_prefix = 'SPOTIFY_'
