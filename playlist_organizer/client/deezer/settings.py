from pydantic import BaseSettings


class DeezerSettings(BaseSettings):
    api_host: str = 'https://api.deezer.com'

    user_info_path: str = 'user/me'
    playlists_path: str = 'user/me/playlists'
    playlist_tracks_path: str = 'playlist/{}/tracks'

    @property
    def user_info_url(self) -> str:
        return f'{self.api_host}/{self.user_info_path}'

    @property
    def playlists_url(self) -> str:
        return f'{self.api_host}/{self.playlists_path}'

    @property
    def playlists_tracks_url(self) -> str:
        return f'{self.api_host}/{self.playlist_tracks_path}'

    class Config:
        env_prefix = 'DEEZER_'
