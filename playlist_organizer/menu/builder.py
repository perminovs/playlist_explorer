from __future__ import annotations

import enum
import logging
from dataclasses import dataclass, field
from typing import Any, Callable, Dict, List, Union
from uuid import uuid4

import inquirer
import typer

from playlist_organizer.client.base import IPlatformClient, Track
from playlist_organizer.client.deezer.client import DeezerClient
from playlist_organizer.client.spotify.client import SpotifyClient
from playlist_organizer.matcher import MatchResult, TrackMatcher
from playlist_organizer.menu.factory import Factory
from playlist_organizer.menu.render import MAX_LEN, render_matches
from playlist_organizer.utils import pprint_json

MenuAction = Callable[[], None]
logger = logging.getLogger(__name__)


@dataclass
class MenuItem:
    title: str
    choices: Dict[str, Union[MenuAction, MenuItem]]
    id: str = field(default_factory=lambda: str(uuid4()))


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
            TopLevelMenu.MATCH_PLAYLISTS: lambda: _match_playlists(  # type: ignore
                factory.deezer_client, factory.spotify_client, factory.track_matcher
            ),
        },
    )


def _playlist_tracks(client: IPlatformClient[Any]) -> None:
    tracks = _get_playlist_tracks(client, 'Which one?')
    typer.secho(f'Tracks total: {len(tracks)}', fg='green')
    for t in tracks:
        typer.secho(str(t), fg='white')


def _match_playlists(deezer_client: DeezerClient, spotify_client: SpotifyClient, matcher: TrackMatcher) -> MenuItem:
    deezer_tracks = _get_playlist_tracks(deezer_client, message='Choose playlist from Deezer')
    spotify_tracks = _get_playlist_tracks(spotify_client, message='Choose playlist from Spotify')
    matches = matcher.match(deezer_tracks, spotify_tracks)

    return _process_match_result(matches)


def _process_match_result(matches: MatchResult) -> MenuItem:
    render_matches(matches)
    logger.debug(
        'Handle matches with %s pairs, %s only Deezer tracks and %s only Spotify tracks',
        len(matches.found),
        len(matches.only_left),
        len(matches.only_right),
    )

    additional_choices = {}
    if bool(matches.only_left) and bool(matches.only_right):
        additional_choices = {'Match track by handle': lambda: _handle_link_tracks(matches)}

    return MenuItem(
        title='And what next?',
        choices={
            **additional_choices,  # type: ignore
            'Everything is ok! Create playlist copy': lambda: _create_playlist_copy(matches),
        },
        id='_process_match_result',
    )


def _create_playlist_copy(matches: MatchResult) -> None:
    render_matches(matches)
    typer.secho('LOL KEK CHEBUREK', bg='white')


def _handle_link_tracks(matches: MatchResult) -> MenuItem:
    deezer_track = _choose_track('Which one from Deezer?', matches.only_left)
    spotify_track = _choose_track('Which one from Spotify?', matches.only_right)

    matches.found[deezer_track] = spotify_track
    matches.only_left.remove(deezer_track)
    matches.only_right.remove(spotify_track)

    return _process_match_result(matches)


def _choose_track(title: str, track_list: List[Track]) -> Track:
    track_map = dict(enumerate(track_list, start=1))
    answer: str = inquirer.list_input(
        title,
        choices=[f'{idx}. {track.to_brief_str(MAX_LEN - 3)}' for idx, track in track_map.items()],
    )
    track_id = int(answer[: answer.find('.')])  # no, I don't like regexps
    return track_map[track_id]


def _get_playlist_tracks(client: IPlatformClient[Any], message: str) -> List[Track]:
    playlists = client.get_playlist_names()
    target = inquirer.list_input(message, choices=playlists)
    return client.get_playlist_tracks(target)
