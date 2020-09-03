from functools import lru_cache
from typing import List

import click
import httpx

from auth.deezer import DeezerAuthenticator
from deezer.entities import PlaylistsResponse, PlaylistDetail, Playlist
from deezer.settings import DeezerSettings
from utils import pprint_resp


class DeezerClient:
    def __init__(self, settings: DeezerSettings, authenticator: DeezerAuthenticator):
        self._settings = settings
        self._authenticator = authenticator

    def user_info(self):
        resp = httpx.get(
            self._settings.user_info_url,
            params={'access_token': self._authenticator.token},
        )
        resp.raise_for_status()

        info = resp.json()
        pprint_resp(resp)
        if any(key not in info for key in ('id', 'email', 'type')):
            raise ValueError(f'Token is not valid, got json:\n{info}')

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
            found = ', '.join((f'<{p.title}>' for p in playlist_info))
            raise ValueError(f'Playlist {name} was not found\n{found}')

        resp = httpx.get(
            self._settings.playlists_info_url.format(target_playlist_id),
            params={'access_token': self._authenticator.token, 'limit': 200},
        )
        resp.raise_for_status()
        target_playlist: PlaylistDetail = PlaylistDetail.parse_obj(resp.json())
        for track in target_playlist.tracks.data:
            click.secho(str(track), fg='white')
