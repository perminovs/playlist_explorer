from functools import lru_cache
from typing import List

import httpx

from deezer.auth import DeezerAuthenticator
from deezer.entities import PlaylistsResponse, PlaylistDetail, Playlist
from deezer.settings import DeezerSettings


class DeezerClient:
    def __init__(
        self,
        settings: DeezerSettings,
        authenticator: DeezerAuthenticator
    ):
        self._settings = settings
        self._authenticator = authenticator

    @lru_cache()
    def get_playlist_list(self) -> List[Playlist]:
        resp = httpx.get(
            self._settings.playlists_url,
            params={'access_token': self._authenticator.token, 'limit': 200},
        )
        resp.raise_for_status()
        playlist_info: PlaylistsResponse = PlaylistsResponse.parse_obj(resp.json())
        return playlist_info.data

    @lru_cache()
    def get_playlist_info(self, name: str):
        playlist_info = self.get_playlist_list()

        for playlist in playlist_info:
            if playlist.title == name:
                target_playlist_id = playlist.id
                break
        else:
            found = ', '.join((f'<{p.title}>' for p in playlist_info.data))
            raise ValueError(f'Playlist {name} was not found\n{found}')

        resp = httpx.get(
            self._settings.playlists_info_url.format(target_playlist_id),
            params={'access_token': self._authenticator.token, 'limit': 200},
        )
        resp.raise_for_status()
        target_playlist: PlaylistDetail = PlaylistDetail.parse_obj(resp.json())
        for track in target_playlist.tracks.data:
            print(track)
