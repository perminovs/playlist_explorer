from functools import cached_property, lru_cache
from typing import Any, Dict, List

import httpx
import typer

from organizer.client.auth.deezer import DeezerAuthenticator
from organizer.client.base import IPlatformClient
from organizer.client.deezer.entities import Playlist, PlaylistDetail, PlaylistsResponse
from organizer.client.deezer.settings import DeezerSettings
from organizer.utils import pprint_json


class DeezerClient(IPlatformClient[Playlist]):
    def __init__(self, settings: DeezerSettings, authenticator: DeezerAuthenticator) -> None:
        self._settings = settings
        self._authenticator = authenticator

    def user_info(self) -> None:
        pprint_json(self._user_info)

    @cached_property
    def _user_info(self) -> Dict[str, Any]:
        resp = httpx.get(
            self._settings.user_info_url,
            params={'access_token': self._authenticator.token},
        )
        resp.raise_for_status()
        return resp.json()

    def get_playlist_list(self) -> List[Playlist]:  # because mypy + generics + lru_cache returns false-positive error
        return self._playlist_response.data

    @cached_property
    def _playlist_response(self) -> PlaylistsResponse:
        resp = httpx.get(
            self._settings.playlists_url,
            params={'access_token': self._authenticator.token, 'limit': 200},
        )
        resp.raise_for_status()
        return PlaylistsResponse.parse_obj(resp.json())

    def get_playlist_names(self) -> List[str]:
        return [p.title for p in self.get_playlist_list()]

    @lru_cache()
    def _playlist_id_by_name(self, name: str) -> str:
        for playlist in self.get_playlist_list():
            if playlist.title == name:
                return playlist.id

        raise ValueError(f'Playlist "{name}" was not found')

    def show_playlist_info(self, name: str) -> None:
        playlist_id = self._playlist_id_by_name(name)

        resp = httpx.get(
            self._settings.playlists_info_url.format(playlist_id),
            params={'access_token': self._authenticator.token, 'limit': 200},
        )
        resp.raise_for_status()
        target_playlist: PlaylistDetail = PlaylistDetail.parse_obj(resp.json())
        typer.secho(f'Tracks total: {len(target_playlist.tracks.data)}', fg='green')
        for track in target_playlist.tracks.data:
            typer.secho(str(track), fg='white')
