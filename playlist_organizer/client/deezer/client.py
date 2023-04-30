from functools import cache, cached_property
from typing import Any, Dict, List, Type, TypeVar, cast

import httpx

from playlist_organizer.client.auth.deezer import DeezerAuthenticator
from playlist_organizer.client.base import BaseClient, Track
from playlist_organizer.client.deezer.entities import PaginatedResponse, Playlist, PlaylistsResponse, PlaylistTracks
from playlist_organizer.client.deezer.settings import DeezerSettings

PaginatedResponseType = TypeVar('PaginatedResponseType', bound=PaginatedResponse)


class DeezerClient(BaseClient[Playlist]):
    def __init__(self, settings: DeezerSettings, authenticator: DeezerAuthenticator) -> None:
        self._settings = settings
        super().__init__(authenticator)

    @cached_property
    def user_info(self) -> Dict[str, Any]:
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

    def get_playlist_tracks(self, name: str) -> List[Track]:
        playlist_id = self._playlist_id_by_name(name)

        tracks = self._fetch_paginated(
            url=self._settings.playlists_tracks_url.format(playlist_id),
            limit=200,
            model_cls=PlaylistTracks,
        )
        return [Track.from_deezer(t) for t in tracks]

    def _fetch_paginated(self, url: str, limit: int, model_cls: Type[PaginatedResponseType]) -> List[Any]:
        return _fetch_paginated(url, limit, model_cls, self._authenticator.token)


@cache
def _fetch_paginated(url: str, limit: int, model_cls: Type[PaginatedResponseType], token: str) -> List[Any]:
    acc = []
    while True:
        if not url:
            break
        resp = httpx.get(url, params={'access_token': token, 'limit': limit})
        resp.raise_for_status()
        page = model_cls.parse_obj(resp.json())
        acc.extend(page.data)
        url = page.next  # type: ignore
    return acc
