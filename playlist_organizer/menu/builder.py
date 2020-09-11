from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Union

import inquirer
import typer

from playlist_organizer.client.base import IPlatformClient, Track
from playlist_organizer.client.deezer.client import DeezerClient
from playlist_organizer.client.spotify.client import SpotifyClient
from playlist_organizer.matcher import TrackMatcher
from playlist_organizer.menu.factory import Factory
from playlist_organizer.menu.render import render_matches
from playlist_organizer.utils import pprint_json

MenuAction = Callable[[], None]


@dataclass
class MenuItem:
    title: str
    choices: Dict[str, Union[MenuAction, MenuItem]]


def _(*args: Any, **kwargs: Any) -> None:  # pylint: disable=W0613
    pass


class TopLevelMenu(str, enum.Enum):
    DEEZER = 'Deezer'
    SPOTIFY = 'Spotify'
    MATCH_PLAYLISTS = 'Match playlist tracks'


class DeezerOptions(str, enum.Enum):
    AUTH = 'Authentication'
    USER_INFO = 'User info'
    PLAYLIST_INFO = 'Playlist info'


class SpotifyOptions(str, enum.Enum):
    AUTH = 'Authentication'
    USER_INFO = 'User info'
    PLAYLIST_INFO = 'Playlist info'


def build_menu(factory: Factory) -> MenuItem:
    deezer_menu = MenuItem(
        title='What to do with Deezer?',
        choices={
            DeezerOptions.AUTH: lambda: _(factory.deezer_auth.token),
            DeezerOptions.USER_INFO: lambda: pprint_json(factory.deezer_client.user_info),
            DeezerOptions.PLAYLIST_INFO: lambda: _playlist_tracks(factory.deezer_client),
        },
    )
    spotify_menu = MenuItem(
        title='What to do with Spotify?',
        choices={
            SpotifyOptions.AUTH: lambda: _(factory.spotify_auth.token),
            SpotifyOptions.USER_INFO: lambda: typer.secho(str(factory.spotify_client.current_user), fg='white'),
            SpotifyOptions.PLAYLIST_INFO: lambda: _playlist_tracks(factory.spotify_client),
        },
    )
    return MenuItem(
        title='What to do?',
        choices={
            TopLevelMenu.DEEZER: deezer_menu,
            TopLevelMenu.SPOTIFY: spotify_menu,
            TopLevelMenu.MATCH_PLAYLISTS: lambda: _match_playlists(
                factory.deezer_client, factory.spotify_client, factory.track_matcher
            ),
        },
    )


def _playlist_tracks(client: IPlatformClient[Any]) -> None:
    tracks = _get_playlist_tracks(client, 'Which one?')
    typer.secho(f'Tracks total: {len(tracks)}', fg='green')
    for t in tracks:
        typer.secho(str(t), fg='white')


def _match_playlists(deezer_client: DeezerClient, spotify_client: SpotifyClient, matcher: TrackMatcher) -> None:
    deezer_tracks = _get_playlist_tracks(deezer_client, message='Choose playlist from Deezer')
    spotify_tracks = _get_playlist_tracks(spotify_client, message='Choose playlist from Spotify')
    matches = matcher.match(deezer_tracks, spotify_tracks)

    render_matches(matches)


def _get_playlist_tracks(client: IPlatformClient[Any], message: str) -> List[Track]:
    playlists = client.get_playlist_names()
    target = inquirer.list_input(message, choices=playlists)
    return client.get_playlist_tracks(target)
