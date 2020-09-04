from pydantic import BaseSettings


class DeezerSettings(BaseSettings):
    api_host: str = 'https://api.deezer.com'

    user_info_path: str = 'user/me'
    playlists_path: str = 'playlists'
    playlist_info_path: str = 'playlist/{}'

    @property
    def user_info_url(self) -> str:
        return f'{self.api_host}/{self.user_info_path}'

    @property
    def playlists_url(self) -> str:
        return f'{self.user_info_url}/{self.playlists_path}'

    @property
    def playlists_info_url(self) -> str:
        return f'{self.api_host}/{self.playlist_info_path}'

    class Config:
        env_prefix = 'DEEZER_'
