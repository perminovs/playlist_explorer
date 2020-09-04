import enum
import logging

import inquirer
import typer

from playlist_order.auth.deezer import DeezerAuthenticator
from playlist_order.auth.settings import DeezerAuthSettings, SpotifyAuthSettings
from playlist_order.auth.spotify import SpotifyAuthenticator
from playlist_order.deezer.client import DeezerClient
from playlist_order.deezer.settings import DeezerSettings
from playlist_order.spotify.client import SpotifyClient
from playlist_order.spotify.settings import SpotifySettings
from playlist_order.utils import create_settings

app = typer.Typer()
logger = logging.getLogger(__name__)
EXIT = 'EXIT'


class DeezerOptions(str, enum.Enum):
    AUTH = 'Deezer: Авторизация'
    USER_INFO = 'Deezer: Информация о пользователе'
    PLAYLIST_INFO = 'Deezer: Информация о плейлисте'


class SpotifyOptions(str, enum.Enum):
    AUTH = 'Spotify: Авторизация'
    USER_INFO = 'Spotify: Информация о пользователе'


class LogLevel(str, enum.Enum):
    DEBUG = logging._levelToName[logging.DEBUG]
    INFO = logging._levelToName[logging.INFO]
    WARNING = logging._levelToName[logging.WARNING]
    ERROR = logging._levelToName[logging.ERROR]


@app.command()
def main(log_level: LogLevel = LogLevel.INFO) -> None:
    logging.basicConfig(level=log_level.value, format='%(asctime)s [%(levelname)s]: %(message)s')

    deezer_auth_settings = create_settings(DeezerAuthSettings, '.env')
    deezer_auth = DeezerAuthenticator(deezer_auth_settings)
    deezer_settings = DeezerSettings()
    deezer_client = DeezerClient(settings=deezer_settings, authenticator=deezer_auth)

    spotify_auth_settings = create_settings(SpotifyAuthSettings, '.env')
    spotify_auth = SpotifyAuthenticator(spotify_auth_settings)
    settings = SpotifySettings()
    spotify_client = SpotifyClient(settings=settings, authenticator=spotify_auth)

    mapping = {
        DeezerOptions.AUTH: lambda: deezer_auth.token,
        DeezerOptions.USER_INFO: deezer_client.user_info,
        DeezerOptions.PLAYLIST_INFO: lambda: playlist_info(deezer_client),
        SpotifyOptions.AUTH: lambda: spotify_auth.token,
        SpotifyOptions.USER_INFO: spotify_client.user_info,
    }

    choices = list(DeezerOptions) + list(SpotifyOptions) + [EXIT]  # type: ignore
    while True:
        option = inquirer.list_input(message='What to do?', choices=choices)
        if not option or option == EXIT:
            return

        func = mapping[option]
        func()


def playlist_info(client: DeezerClient) -> None:
    playlists = client.get_playlist_list()
    target = inquirer.list_input('Which one?', choices=[p.title for p in playlists])
    client.get_playlist_info(target)


if __name__ == '__main__':
    app()
