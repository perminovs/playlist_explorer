from __future__ import annotations

import enum
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Tuple, Union

import inquirer
import typer
from inquirer.render import ConsoleRender
from inquirer.themes import GreenPassion, term

from playlist_organizer.client.base import IPlatformClient, Track
from playlist_organizer.client.deezer.client import DeezerClient
from playlist_organizer.client.spotify.client import SpotifyClient
from playlist_organizer.matcher import MatchResult, TrackMatcher
from playlist_organizer.menu.render import MAX_LEN, render_matches
from playlist_organizer.utils import Stack, pprint_json

MenuAction = Callable[[], None]
logger = logging.getLogger(__name__)

theme = GreenPassion()
theme.List.unselected_color = term.yellow
render = ConsoleRender(theme=theme)


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


class Menu:
    def __init__(
        self,
        deezer_client: DeezerClient,
        spotify_client: SpotifyClient,
        track_matcher: TrackMatcher,
    ) -> None:
        self._deezer_client = deezer_client
        self._spotify_client = spotify_client
        self._track_matcher = track_matcher
        self._matches: List[MatchResult] = []

    @property
    def top_level_menu_item(self) -> MenuItem:
        deezer_menu = MenuItem(
            title='What to do with Deezer?',
            choices={
                DeezerOptions.AUTH: lambda: _(self._deezer_client.token),
                DeezerOptions.USER_INFO: lambda: pprint_json(self._deezer_client.user_info, fg='white'),
                DeezerOptions.PLAYLIST_INFO: lambda: _playlist_tracks(self._deezer_client),
            },
        )
        spotify_menu = MenuItem(
            title='What to do with Spotify?',
            choices={
                SpotifyOptions.AUTH: lambda: _(self._spotify_client.token),
                SpotifyOptions.USER_INFO: lambda: typer.secho(str(self._spotify_client.current_user), fg='white'),
                SpotifyOptions.PLAYLIST_INFO: lambda: _playlist_tracks(self._spotify_client),
            },
        )
        return MenuItem(
            title='What to do?',
            choices={
                TopLevelMenu.DEEZER: deezer_menu,
                TopLevelMenu.SPOTIFY: spotify_menu,
                TopLevelMenu.MATCH_PLAYLISTS: self._match_playlists,
            },
        )

    def run_menu_loop(self) -> None:  # pylint: disable=R0915 R0914
        _exit = 'EXIT'
        _back = 'BACK'

        current_menu = self.top_level_menu_item
        menu_history = Stack[MenuItem]()
        while True:  # pylint: disable=R1702
            menu_choices = current_menu.choices.copy()
            logger.debug('In memory matches:\n%s', '; '.join(m.name for m in self._matches))
            # TODO рендерить историю плейлистов только на главной
            matches_choices = {
                f'Process {m.name} ({m.created_at})': lambda m=m: self._process_match_result(m) for m in self._matches
            }
            menu_choices.update(matches_choices)  # type: ignore

            additional_choices = [_exit] if menu_history.is_empty() else [_back, _exit]
            choices = list(menu_choices) + additional_choices  # type: ignore
            option = inquirer.list_input(message=current_menu.title, choices=choices, render=render)

            if not option or option == _exit:
                return

            if option == _back:
                current_menu = menu_history.pop()
                continue

            chosen = menu_choices[option]

            if isinstance(chosen, MenuItem):
                menu_history.push(current_menu)
                current_menu = chosen
            elif callable(chosen):
                try:
                    next_item = chosen()
                    if isinstance(next_item, MenuItem):
                        menu_history.push(current_menu)
                        current_menu = next_item
                except Exception:  # pylint: disable=W0703
                    logger.exception('Something went wrong, try again')
            else:
                raise RuntimeError('Option not found')

    def _process_match_result(self, matches: MatchResult) -> MenuItem:
        render_matches(matches)
        logger.debug(
            'Handle matches with %s pairs, %s only Deezer tracks and %s only Spotify tracks',
            len(matches.found),
            len(matches.only_left),
            len(matches.only_right),
        )

        additional_choices = {}
        if bool(matches.only_left) and bool(matches.only_right):
            additional_choices = {'Match track by handle': lambda: self._handle_link_tracks(matches)}

        return MenuItem(
            title='And what next?',
            choices={
                **additional_choices,  # type: ignore
                'Everything is ok! Create playlist copy': lambda: self._create_playlist_copy(matches),
            },
        )

    def _match_playlists(self) -> None:
        deezer_name, deezer_tracks = _get_playlist_tracks(self._deezer_client, message='Choose playlist from Deezer')
        spotify_name, spotify_tracks = _get_playlist_tracks(
            self._spotify_client, message='Choose playlist from Spotify'
        )
        matches = self._track_matcher.match(deezer_tracks, spotify_tracks)
        matches.name = f'{deezer_name} -> {spotify_name}'
        self._matches.append(matches)

    def _create_playlist_copy(self, matches: MatchResult) -> None:
        render_matches(matches)
        typer.secho('LOL KEK CHEBUREK', bg='white')

    def _handle_link_tracks(self, matches: MatchResult) -> None:
        deezer_track = _choose_track('Which one from Deezer?', matches.only_left)
        spotify_track = _choose_track('Which one from Spotify?', matches.only_right)

        matches.found[deezer_track] = spotify_track
        matches.only_left.remove(deezer_track)
        matches.only_right.remove(spotify_track)

        render_matches(matches)


def _choose_track(title: str, track_list: List[Track]) -> Track:
    track_map = dict(enumerate(track_list, start=1))
    answer: str = inquirer.list_input(
        title,
        choices=[f'{idx}. {track.to_brief_str(MAX_LEN - 3)}' for idx, track in track_map.items()],
    )
    track_id = int(answer[: answer.find('.')])  # no, I don't like regexps
    return track_map[track_id]


def _playlist_tracks(client: IPlatformClient[Any]) -> None:
    _, tracks = _get_playlist_tracks(client, 'Which one?')
    typer.secho(f'Tracks total: {len(tracks)}', fg='green')
    for t in tracks:
        typer.secho(str(t), fg='white')


def _get_playlist_tracks(client: IPlatformClient[Any], message: str) -> Tuple[str, List[Track]]:
    playlists = client.get_playlist_names()
    target = inquirer.list_input(message, choices=playlists)
    return target, client.get_playlist_tracks(target)
