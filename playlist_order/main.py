import enum
import logging

import inquirer
import click
from pydantic import ValidationError

from deezer.auth import DeezerAuthenticator
from deezer.client import DeezerClient
from deezer.settings import DeezerSettings

logger = logging.getLogger(__name__)


class DeezerOptions(str, enum.Enum):
    AUTH = 'Авторизация'
    USER_INFO = 'Информация о пользователе'
    PLAYLIST_INFO = 'Информация о плейлисте'


LOG_LEVELS = [logging.DEBUG, logging.INFO, logging.WARNING, logging.ERROR]
_lvl2name = lambda x: logging._levelToName[x]


@click.command()
@click.option('--log-level', default=_lvl2name(logging.INFO), type=click.Choice([_lvl2name(n) for n in LOG_LEVELS]))
def main(log_level):
    logging.basicConfig(level=log_level, format='%(asctime)s [%(levelname)s]: %(message)s')

    try:
        settings = DeezerSettings()
        logger.debug('Got settings without .env file')
    except ValidationError:
        settings = DeezerSettings(_env_file='.env')
        logger.debug('Got settings from .env file')

    deezer_auth = DeezerAuthenticator(settings)
    client = DeezerClient(settings=settings, authenticator=deezer_auth)

    mapping = {
        DeezerOptions.AUTH: lambda: deezer_auth.token,
        DeezerOptions.USER_INFO: deezer_auth.user_info,
        DeezerOptions.PLAYLIST_INFO: lambda: playlist_info(client),
    }

    while True:
        option = inquirer.list_input(message='Deezer', choices=list(DeezerOptions) + [None])
        if not option:
            return

        func = mapping[option]
        func()


def playlist_info(client: DeezerClient):
    playlists = client.get_playlist_list()
    target = inquirer.list_input('Which one?', choices=[p.title for p in playlists])
    client.get_playlist_info(target)


if __name__ == '__main__':
    main()
