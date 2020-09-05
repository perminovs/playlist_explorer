from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Callable, Dict, Union

import inquirer
import typer

from organizer.deezer.client import DeezerClient
from organizer.factory.clients import ClientFactory
from organizer.spotify.client import SpotifyClient

MenuAction = Callable[[], None]


@dataclass
class MenuItem:
    title: str
    choices: Dict[str, Union[MenuAction, MenuItem]]


def auth_func(token_attr: str) -> None:
    typer.secho('Auth success', fg='white')


class TopLevelMenu(str, enum.Enum):
    DEEZER = 'Deezer'
    SPOTIFY = 'Spotify'


class DeezerOptions(str, enum.Enum):
    AUTH = 'Authentication'
    USER_INFO = 'User info'
    PLAYLIST_INFO = 'Playlist info'


class SpotifyOptions(str, enum.Enum):
    AUTH = 'Authentication'
    USER_INFO = 'User info'
    PLAYLIST_INFO = 'Playlist info'


def build_menu(client_factory: ClientFactory) -> MenuItem:
    deezer_menu = MenuItem(
        title='What to do with Deezer?',
        choices={
            DeezerOptions.AUTH: lambda: auth_func(client_factory.deezer_auth.token),
            DeezerOptions.USER_INFO: client_factory.deezer_client.user_info,
            DeezerOptions.PLAYLIST_INFO: lambda: playlist_tracks(client_factory.deezer_client),
        },
    )
    spotify_menu = MenuItem(
        title='What to do with Spotify?',
        choices={
            SpotifyOptions.AUTH: lambda: auth_func(client_factory.spotify_auth.token),
            SpotifyOptions.USER_INFO: client_factory.spotify_client.user_info,
            SpotifyOptions.PLAYLIST_INFO: lambda: playlist_tracks(client_factory.spotify_client),
        },
    )
    return MenuItem(
        title='What to do?',
        choices={
            TopLevelMenu.DEEZER: deezer_menu,
            TopLevelMenu.SPOTIFY: spotify_menu,
        },
    )


def playlist_tracks(client: Union[DeezerClient, SpotifyClient]) -> None:
    playlists = client.get_playlist_list()
    target = inquirer.list_input('Which one?', choices=[p.title for p in playlists])
    client.get_playlist_info(target)
