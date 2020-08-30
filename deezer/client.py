import json

import httpx

from deezer.auth import DeezerAuthenticator
from deezer.entities import PlaylistsResponse, PlaylistDetail
from deezer.settings import DeezerSettings


class DeezerClient:
    def __init__(
        self,
        settings: DeezerSettings,
        authenticator: DeezerAuthenticator
    ):
        self._settings = settings
        self._authenticator = authenticator

    def get_playlist_info(self, name: str):
        resp = httpx.get(
            self._settings.playlists_url,
            params={'access_token': self._authenticator.token, 'limit': 200},
        )
        resp.raise_for_status()
        playlist_info: PlaylistsResponse = PlaylistsResponse.parse_obj(resp.json())

        for playlist in playlist_info.data:
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
        # pprint_resp(resp)
        playlist: PlaylistDetail = PlaylistDetail.parse_obj(resp.json())
        for track in playlist.tracks.data:
            print(track)


def pprint_resp(resp):
    print(json.dumps(resp.json(), ensure_ascii=False, indent=4, sort_keys=True))
