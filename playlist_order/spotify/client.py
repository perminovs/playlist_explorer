import httpx

from auth.spotify import SpotifyAuthenticator
from utils import pprint_resp
from spotify.settings import SpotifySettings


class SpotifyClient:
    def __init__(self, settings: SpotifySettings, authenticator: SpotifyAuthenticator):
        self._settings = settings
        self._authenticator = authenticator

    def user_info(self):
        me = httpx.get(self._settings.user_info_url, headers={'Authorization': f'Bearer {self._authenticator.token}'})
        me.raise_for_status()
        pprint_resp(me)
