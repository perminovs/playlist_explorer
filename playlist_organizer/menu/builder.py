from __future__ import annotations

import enum
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Union

import inquirer
import typer
from colorclass import Color
from terminaltables import AsciiTable

from playlist_organizer.client.base import IPlatformClient, Track
from playlist_organizer.client.deezer.client import DeezerClient
from playlist_organizer.client.spotify.client import SpotifyClient
from playlist_organizer.matcher import MatchResult, TrackMatcher
from playlist_organizer.menu.factory import Factory

MenuAction = Callable[[], None]
MAX_LEN = 93


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
            DeezerOptions.USER_INFO: factory.deezer_client.user_info,
            DeezerOptions.PLAYLIST_INFO: lambda: _playlist_tracks(factory.deezer_client),
        },
    )
    spotify_menu = MenuItem(
        title='What to do with Spotify?',
        choices={
            SpotifyOptions.AUTH: lambda: _(factory.spotify_auth.token),
            SpotifyOptions.USER_INFO: factory.spotify_client.user_info,
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

    _render_matches(matches)


def _get_playlist_tracks(client: IPlatformClient[Any], message: str) -> List[Track]:
    playlists = client.get_playlist_names()
    target = inquirer.list_input(message, choices=playlists)
    return client.get_playlist_tracks(target)


def _render_matches(match_result: MatchResult) -> None:
    table_headers = [[_c('Deezer', color='automagenta'), _c('Spotify', color='automagenta')]]
    table_body = [[d.to_brief_str(MAX_LEN), s.to_brief_str(MAX_LEN)] for d, s in match_result.found.items()]
    found = AsciiTable(table_headers + table_body)
    typer.secho(found.table)

    _render_single('Deezer only', match_result.only_left)
    _render_single('Spotify only', match_result.only_right)


def _c(text: str, color: str) -> str:
    return Color(f'{{{color}}}{text}{{/{color}}}')


def _render_single(title: str, tracks: List[Track]) -> None:
    header = [[_c(title, color='automagenta')]]
    body = [[t.to_brief_str(MAX_LEN * 2)] for t in tracks]

    data = AsciiTable(header + body)
    typer.secho(data.table)
