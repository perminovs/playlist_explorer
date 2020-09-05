from functools import lru_cache
from typing import Dict, List, Type, TypeVar

import httpx
import typer

from organizer.auth.spotify import SpotifyAuthenticator
from organizer.spotify.entities import BasePaginatedResponse, Playlist, PlaylistDetail, PlaylistsAnswer
from organizer.spotify.settings import SpotifySettings
from organizer.utils import pprint_json

AnyPaginatedResponse = TypeVar('AnyPaginatedResponse', bound=BasePaginatedResponse)


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
        playlist_answers: List[PlaylistsAnswer] = self._fetch_with_pagination(
            url=self._settings.playlists_url,
            limit=50,
            model_cls=PlaylistsAnswer,
        )

        playlists: List[Playlist] = []
        for answer in playlist_answers:
            playlists.extend(answer.items)
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

        playlist_responses: List[PlaylistDetail] = self._fetch_with_pagination(
            url=self._settings.playlists_info_url.format(playlist_id),
            limit=100,
            model_cls=PlaylistDetail,
        )

        for playlist in playlist_responses:
            for track in playlist.tracks:
                typer.secho(str(track), fg='white')

    def _fetch_with_pagination(
        self, url: str, limit: int, model_cls: Type[AnyPaginatedResponse]
    ) -> List[AnyPaginatedResponse]:
        result: List[AnyPaginatedResponse] = []
        while True:
            if not url:
                break

            resp = httpx.get(url, params={'limit': limit}, headers=self._headers)
            resp.raise_for_status()
            basket = model_cls.parse_obj(resp.json())
            result.append(basket)
            url = basket.next  # type: ignore

        return result
