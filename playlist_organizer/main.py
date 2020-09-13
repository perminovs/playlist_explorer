import enum
import logging

import typer

from playlist_organizer.client.auth.deezer import DeezerAuthenticator
from playlist_organizer.client.auth.settings import DeezerAuthSettings, SpotifyAuthSettings
from playlist_organizer.client.auth.spotify import SpotifyAuthenticator
from playlist_organizer.client.deezer.client import DeezerClient
from playlist_organizer.client.deezer.settings import DeezerSettings
from playlist_organizer.client.spotify.client import SpotifyClient
from playlist_organizer.client.spotify.settings import SpotifySettings
from playlist_organizer.matcher import TrackMatcher
from playlist_organizer.menu.builder import Menu
from playlist_organizer.utils import create_settings

app = typer.Typer()
logger = logging.getLogger(__name__)


class LogLevel(str, enum.Enum):
    DEBUG = logging._levelToName[logging.DEBUG]  # pylint: disable=W0212
    INFO = logging._levelToName[logging.INFO]  # pylint: disable=W0212
    WARNING = logging._levelToName[logging.WARNING]  # pylint: disable=W0212
    ERROR = logging._levelToName[logging.ERROR]  # pylint: disable=W0212


@app.command()
def main(log_level: LogLevel = LogLevel.INFO) -> None:
    logging.basicConfig(level=log_level.value, format='%(asctime)s [%(levelname)s]: %(message)s')

    deezer_settings = create_settings(DeezerAuthSettings, '.env')
    deezer_authenticator = DeezerAuthenticator(deezer_settings)

    spotify_settings = create_settings(SpotifyAuthSettings, '.env')
    spotify_authenticator = SpotifyAuthenticator(spotify_settings)

    menu = Menu(
        deezer_client=DeezerClient(settings=DeezerSettings(), authenticator=deezer_authenticator),
        spotify_client=SpotifyClient(settings=SpotifySettings(), authenticator=spotify_authenticator),
        track_matcher=TrackMatcher(),
    )
    menu.run_menu_loop()
