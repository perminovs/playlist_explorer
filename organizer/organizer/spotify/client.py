from __future__ import annotations

from functools import cached_property, lru_cache, wraps
from typing import TYPE_CHECKING, List

import tekore as tk
import typer

if TYPE_CHECKING:
    from tekore._model import PlaylistTrack, PrivateUser, SimplePlaylist

    from organizer.auth.spotify import SpotifyAuthenticator
    from organizer.spotify.settings import SpotifySettings


def _ensure_auth(func):  # type: ignore
    @wraps(func)
    def _inner(self: SpotifyClient, *args, **kwargs):  # type: ignore
        if not self._spotify:
            self._spotify = tk.Spotify(token=self._authenticator.token)
        return func(self, *args, **kwargs)

    return _inner


class SpotifyClient:
    def __init__(self, settings: SpotifySettings, authenticator: SpotifyAuthenticator):
        self._settings = settings
        self._authenticator = authenticator
        self._spotify: tk.Spotify = None

    @_ensure_auth
    def user_info(self) -> None:
        typer.secho(str(self._current_user), fg='white')

    @cached_property
    @_ensure_auth
    def _current_user(self) -> PrivateUser:
        return self._spotify.current_user()  # type: ignore

    @_ensure_auth
    def get_playlist_list(self) -> List[SimplePlaylist]:
        return _fetch_paginated(self._spotify.playlists, limit=50, user_id=self._current_user.id)  # type: ignore

    def get_playlist_names(self) -> List[str]:
        return [p.name for p in self.get_playlist_list()]

    @_ensure_auth
    def _playlist_id_by_name(self, name: str) -> str:
        for playlist in self.get_playlist_list():
            if playlist.name == name:
                return playlist.id

        raise ValueError(f'Playlist "{name}" was not found')

    @_ensure_auth
    def show_playlist_info(self, name: str) -> None:
        playlist_id = self._playlist_id_by_name(name)

        tracks: List[PlaylistTrack]
        tracks = _fetch_paginated(self._spotify.playlist_items, playlist_id, limit=50)

        typer.secho(f'Tracks total: {len(tracks)}', fg='green')
        for track_info in tracks:
            artists = '; '.join(a.name for a in track_info.track.artists)
            album = track_info.track.album.name
            info = f'{artists} - {track_info.track.name} ({album}) [added: {track_info.added_at}]'
            typer.secho(info, fg='white')


@lru_cache()
def _fetch_paginated(method, *args, limit: int, **kwargs):  # type: ignore
    offset = 0
    acc = []
    while True:
        page = method(*args, limit=limit, offset=offset, **kwargs)
        if not page.items:
            break
        acc.extend(page.items)
        offset += limit
    return acc
