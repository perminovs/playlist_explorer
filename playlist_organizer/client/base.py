from __future__ import annotations

import abc
import enum
from datetime import datetime
from typing import TYPE_CHECKING, Generic, List, TypeVar

from pydantic import BaseModel

if TYPE_CHECKING:
    from tekore._model import PlaylistTrack as SpotifyTrack

    from playlist_organizer.client.deezer.entities import Track as DeezerTrack

PlaylistType = TypeVar('PlaylistType')


class IPlatformClient(Generic[PlaylistType], abc.ABC):
    @abc.abstractmethod
    def get_playlist_list(self) -> List[PlaylistType]:
        pass

    @abc.abstractmethod
    def get_playlist_names(self) -> List[str]:
        pass

    @abc.abstractmethod
    def get_playlist_tracks(self, name: str) -> List[Track]:
        pass


class Platform(str, enum.Enum):
    DEEZER = 'DEEZER'
    SPOTIFY = 'SPOTIFY'


class Track(BaseModel):
    artists: List[str]
    album: str
    title: str
    added_at: datetime
    source: Platform
    external_id: str

    def __str__(self) -> str:
        artists = '; '.join(self.artists)
        return f'{artists} - {self.title} ({self.album}) [added: {self.added_at}]'

    @classmethod
    def from_deezer(cls, track: DeezerTrack) -> Track:
        return cls(
            artists=[track.artist.name],
            album=track.album.title,
            title=track.title,
            added_at=datetime.fromtimestamp(track.time_add),
            source=Platform.DEEZER,
            external_id=str(track.id),
        )

    @classmethod
    def from_spotify(cls, track: SpotifyTrack) -> Track:
        return cls(
            artists=[a.name for a in track.track.artists],
            album=track.track.album.name,
            title=track.track.name,
            added_at=track.added_at,
            source=Platform.SPOTIFY,
            external_id=track.track.id,
        )
