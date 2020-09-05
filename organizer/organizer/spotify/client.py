from functools import lru_cache
from typing import Dict, List, Optional

import httpx
import typer

from organizer.auth.spotify import SpotifyAuthenticator
from organizer.spotify.entities import Playlist, PlaylistDetail, PlaylistsAnswer, TrackInfo
from organizer.spotify.settings import SpotifySettings
from organizer.utils import pprint_json


class SpotifyClient:
    def __init__(self, settings: SpotifySettings, authenticator: SpotifyAuthenticator):
        self._settings = settings
        self._authenticator = authenticator

    @property
    def _headers(self) -> Dict[str, str]:
        return {'Authorization': f'Bearer {self._authenticator.token}'}

    def user_info(self) -> None:
        me = httpx.get(self._settings.user_info_url, headers=self._headers)
        me.raise_for_status()
        pprint_json(me.json())

    @lru_cache()
    def get_playlist_list(self) -> List[Playlist]:
        url: Optional[str] = self._settings.playlists_url
        playlists: List[Playlist] = []
        while True:
            if not url:
                break

            resp = httpx.get(url, params={'limit': 50}, headers=self._headers)
            resp.raise_for_status()
            answer = PlaylistsAnswer.parse_obj(resp.json())
            playlists.extend(answer.items)
            url = answer.next
        return playlists

    @lru_cache()
    def _playlist_id_by_name(self, name: str) -> str:
        playlist_info = self.get_playlist_list()

        for playlist in playlist_info:
            if playlist.title == name:
                return playlist.id

        found = ', '.join((f'<{p.title}>' for p in playlist_info))
        raise ValueError(f'Playlist {name} was not found\n{found}')

    @lru_cache()
    def get_playlist_info(self, name: str) -> None:
        playlist_id = self._playlist_id_by_name(name)

        url: Optional[str] = self._settings.playlists_info_url.format(playlist_id)
        tracks: List[TrackInfo] = []
        while True:
            if not url:
                break

            resp = httpx.get(url, params={'limit': 100}, headers=self._headers)
            resp.raise_for_status()
            target_playlist: PlaylistDetail = PlaylistDetail.parse_obj(resp.json())
            tracks.extend(target_playlist.tracks)
            url = target_playlist.next

        for track in tracks:
            typer.secho(str(track), fg='white')
