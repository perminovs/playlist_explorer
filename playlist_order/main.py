import enum
import logging

import inquirer
import typer
from inquirer.render import ConsoleRender
from inquirer.themes import GreenPassion, term

from playlist_order.auth.deezer import DeezerAuthenticator
from playlist_order.auth.settings import DeezerAuthSettings, SpotifyAuthSettings
from playlist_order.auth.spotify import SpotifyAuthenticator
from playlist_order.deezer.client import DeezerClient
from playlist_order.deezer.settings import DeezerSettings
from playlist_order.spotify.client import SpotifyClient
from playlist_order.spotify.settings import SpotifySettings
from playlist_order.utils import MenuItem, Stack, create_settings

app = typer.Typer()
logger = logging.getLogger(__name__)

theme = GreenPassion()
theme.List.unselected_color = term.yellow
render = ConsoleRender(theme=theme)

EXIT = 'EXIT'
BACK = 'BACK'


class TopLevelMenu(str, enum.Enum):
    DEEZER = 'Deezer'
    SPOTIFY = 'Spotify'


class DeezerOptions(str, enum.Enum):
    AUTH = 'Авторизация'
    USER_INFO = 'Информация о пользователе'
    PLAYLIST_INFO = 'Информация о плейлисте'


class SpotifyOptions(str, enum.Enum):
    AUTH = 'Авторизация'
    USER_INFO = 'Информация о пользователе'


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

    deezer_menu = MenuItem(
        title='What to do with Deezer?',
        choices={
            DeezerOptions.AUTH: lambda: deezer_auth.token,
            DeezerOptions.USER_INFO: deezer_client.user_info,
            DeezerOptions.PLAYLIST_INFO: lambda: playlist_info(deezer_client),
        },
    )
    spotify_menu = MenuItem(
        title='What to do with Spotify?',
        choices={
            SpotifyOptions.AUTH: lambda: spotify_auth.token,
            SpotifyOptions.USER_INFO: spotify_client.user_info,
        },
    )
    top_level_menu = MenuItem(
        title='What to do?',
        choices={
            TopLevelMenu.DEEZER: deezer_menu,
            TopLevelMenu.SPOTIFY: spotify_menu,
        },
    )

    menu_history = Stack()
    current_menu = top_level_menu
    while True:
        additional_choices = [EXIT] if menu_history.is_empty() else [BACK, EXIT]
        choices = list(current_menu.choices) + additional_choices  # type: ignore
        option = inquirer.list_input(message=current_menu.title, choices=choices, render=render)
        if not option or option == EXIT:
            return

        if option == BACK:
            current_menu = menu_history.pop()
            continue

        chosen = current_menu.choices[option]

        if isinstance(chosen, MenuItem):
            menu_history.push(current_menu)
            current_menu = chosen
        elif callable(chosen):
            chosen()
        else:
            raise RuntimeError('Option not found')


def playlist_info(client: DeezerClient) -> None:
    playlists = client.get_playlist_list()
    target = inquirer.list_input('Which one?', choices=[p.title for p in playlists])
    client.get_playlist_info(target)


if __name__ == '__main__':
    app()
