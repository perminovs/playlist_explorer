from functools import cached_property, lru_cache
from typing import Any, Dict, List, Type, TypeVar, cast

import httpx
import typer

from organizer.client.auth.deezer import DeezerAuthenticator
from organizer.client.base import IPlatformClient
from organizer.client.deezer.entities import PaginatedResponse, Playlist, PlaylistsResponse, PlaylistTracks
from organizer.client.deezer.settings import DeezerSettings
from organizer.utils import pprint_json

PaginatedResponseType = TypeVar('PaginatedResponseType', bound=PaginatedResponse)


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

    def get_playlist_list(self) -> List[Playlist]:
        playlists = self._fetch_paginated(self._settings.playlists_url, limit=50, model_cls=PlaylistsResponse)
        return cast(List[Playlist], playlists)

    def get_playlist_names(self) -> List[str]:
        return [p.title for p in self.get_playlist_list()]

    def _playlist_id_by_name(self, name: str) -> str:
        for playlist in self.get_playlist_list():
            if playlist.title == name:
                return playlist.id

        raise ValueError(f'Playlist "{name}" was not found')

    def show_playlist_info(self, name: str) -> None:
        playlist_id = self._playlist_id_by_name(name)

        tracks = self._fetch_paginated(
            url=self._settings.playlists_tracks_url.format(playlist_id),
            limit=200,
            model_cls=PlaylistTracks,
        )

        typer.secho(f'Tracks total: {len(tracks)}', fg='green')
        for track in tracks:
            typer.secho(str(track), fg='white')

    @lru_cache()
    def _fetch_paginated(self, url: str, limit: int, model_cls: Type[PaginatedResponseType]) -> List[Any]:
        acc = []
        while True:
            if not url:
                break
            resp = httpx.get(url, params={'access_token': self._authenticator.token, 'limit': limit})
            resp.raise_for_status()
            page = model_cls.parse_obj(resp.json())
            acc.extend(page.data)
            url = page.next  # type: ignore
        return acc
