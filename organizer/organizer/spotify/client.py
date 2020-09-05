import httpx

from organizer.auth.spotify import SpotifyAuthenticator
from organizer.spotify.settings import SpotifySettings
from organizer.utils import pprint_json


class SpotifyClient:
    def __init__(self, settings: SpotifySettings, authenticator: SpotifyAuthenticator):
        self._settings = settings
        self._authenticator = authenticator

    def user_info(self) -> None:
        me = httpx.get(self._settings.user_info_url, headers={'Authorization': f'Bearer {self._authenticator.token}'})
        me.raise_for_status()
        pprint_json(me.json())
