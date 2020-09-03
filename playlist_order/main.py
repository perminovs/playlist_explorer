import enum
import logging
from typing import Type, TypeVar

import click
import inquirer
from pydantic import ValidationError

from auth.deezer import DeezerAuthenticator
from auth.settings import DeezerAuthSettings, SpotifyAuthSettings
from auth.spotify import SpotifyAuthenticator
from deezer.client import DeezerClient
from deezer.settings import DeezerSettings
from spotify.client import SpotifyClient
from spotify.settings import SpotifySettings

logger = logging.getLogger(__name__)


class DeezerOptions(str, enum.Enum):
    AUTH = 'Deezer: Авторизация'
    USER_INFO = 'Deezer: Информация о пользователе'
    PLAYLIST_INFO = 'Deezer: Информация о плейлисте'


class SpotifyOptions(str, enum.Enum):
    AUTH = 'Spotify: Авторизация'
    USER_INFO = 'Spotify: Информация о пользователе'


EXIT = 'EXIT'
LOG_LEVELS = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]
_lvl2name = lambda x: logging._levelToName[x]
T = TypeVar('T')


def _create_settings(settings_cls: Type[T], env_file: str) -> T:
    try:
        settings = settings_cls()
        logger.debug('Got settings %s without .env file', settings_cls)
    except ValidationError:
        settings = settings_cls(_env_file=env_file)
        logger.debug('Got settings %s from .env file', settings_cls)
    return settings


@click.command()
@click.option('--log-level', default=_lvl2name(logging.INFO), type=click.Choice([_lvl2name(n) for n in LOG_LEVELS]))
def main(log_level):
    logging.basicConfig(level=log_level, format='%(asctime)s [%(levelname)s]: %(message)s')

    deezer_auth_settings = _create_settings(DeezerAuthSettings, '.env')
    deezer_auth = DeezerAuthenticator(deezer_auth_settings)
    deezer_settings = DeezerSettings()
    deezer_client = DeezerClient(settings=deezer_settings, authenticator=deezer_auth)

    spotify_auth_settings = _create_settings(SpotifyAuthSettings, '.env')
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

    choices = list(DeezerOptions) + list(SpotifyOptions) + [EXIT]
    while True:
        option = inquirer.list_input(message='What to do?', choices=choices)
        if not option or option == EXIT:
            return

        func = mapping[option]
        func()


def playlist_info(client: DeezerClient):
    playlists = client.get_playlist_list()
    target = inquirer.list_input('Which one?', choices=[p.title for p in playlists])
    client.get_playlist_info(target)


if __name__ == '__main__':
    main()
