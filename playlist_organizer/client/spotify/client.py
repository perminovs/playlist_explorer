from __future__ import annotations

from functools import cached_property, lru_cache, wraps
from typing import TYPE_CHECKING, List

import tekore as tk
from tekore._model import FullPlaylist, SimplePlaylist

from playlist_organizer.client.base import BaseClient, Track

if TYPE_CHECKING:
    from tekore._model import PlaylistTrack, PrivateUser

    from playlist_organizer.client.auth.spotify import SpotifyAuthenticator
    from playlist_organizer.client.spotify.settings import SpotifySettings


def _ensure_auth(func):  # type: ignore
    @wraps(func)
    def _inner(self: SpotifyClient, *args, **kwargs):  # type: ignore
        if not self._spotify:  # pylint: disable=W0212
            self._spotify = tk.Spotify(token=self._authenticator.token)  # pylint: disable=W0212
        return func(self, *args, **kwargs)

    return _inner


class SpotifyClient(BaseClient[SimplePlaylist]):
    def __init__(self, settings: SpotifySettings, authenticator: SpotifyAuthenticator):
        self._settings = settings
        self._spotify: tk.Spotify = None
        super().__init__(authenticator)

    @cached_property
    @_ensure_auth
    def current_user(self) -> PrivateUser:
        return self._spotify.current_user()  # type: ignore

    @_ensure_auth
    def get_playlist_list(self) -> List[SimplePlaylist]:
        return _fetch_paginated(self._spotify.playlists, limit=50, user_id=self.current_user.id)  # type: ignore

    def get_playlist_names(self) -> List[str]:
        return [p.name for p in self.get_playlist_list()]

    @_ensure_auth
    def _playlist_id_by_name(self, name: str) -> str:
        for playlist in self.get_playlist_list():
            if playlist.name == name:
                return playlist.id

        raise ValueError(f'Playlist "{name}" was not found')

    @_ensure_auth
    def get_playlist_tracks(self, name: str) -> List[Track]:
        playlist_id = self._playlist_id_by_name(name)

        tracks: List[PlaylistTrack]
        tracks = _fetch_paginated(self._spotify.playlist_items, playlist_id, limit=50)
        return [Track.from_spotify(t) for t in tracks]

    @_ensure_auth
    def create_playlist(self, name: str, public: bool = False) -> FullPlaylist:
        return self._spotify.playlist_create(
            user_id=self.current_user.id,
            name=name,
            public=public,
        )

    @_ensure_auth
    def add_playlist_tracks(self, playlist: FullPlaylist, tracks: List[Track]) -> None:
        pass


@lru_cache()
def _fetch_paginated(method, *args, limit: int, **kwargs):  # type: ignore
    offset = 0
    acc = []
    while True:
        page = method(*args, limit=limit, offset=offset, **kwargs)
        acc.extend(page.items)
        offset += limit
        if not page.next:
            break
    return acc
