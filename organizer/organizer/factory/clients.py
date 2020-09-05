from functools import cached_property

from organizer.auth.deezer import DeezerAuthenticator
from organizer.auth.settings import DeezerAuthSettings, SpotifyAuthSettings
from organizer.auth.spotify import SpotifyAuthenticator
from organizer.deezer.client import DeezerClient
from organizer.deezer.settings import DeezerSettings
from organizer.spotify.client import SpotifyClient
from organizer.spotify.settings import SpotifySettings
from organizer.utils import create_settings


class ClientFactory:
    @cached_property
    def _deezer_auth_settings(self) -> DeezerAuthSettings:
        return create_settings(DeezerAuthSettings, '.env')

    @cached_property
    def deezer_auth(self) -> DeezerAuthenticator:
        return DeezerAuthenticator(self._deezer_auth_settings)

    @cached_property
    def deezer_client(self) -> DeezerClient:
        return DeezerClient(settings=DeezerSettings(), authenticator=self.deezer_auth)

    @cached_property
    def _spotify_auth_settings(self) -> SpotifyAuthSettings:
        return create_settings(SpotifyAuthSettings, '.env')

    @cached_property
    def spotify_auth(self) -> SpotifyAuthenticator:
        return SpotifyAuthenticator(self._spotify_auth_settings)

    @cached_property
    def spotify_client(self) -> SpotifyClient:
        return SpotifyClient(settings=SpotifySettings(), authenticator=self.spotify_auth)
