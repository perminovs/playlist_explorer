from datetime import datetime
from typing import TYPE_CHECKING, Any, List, Optional

from pydantic import BaseModel


class PaginatedResponse(BaseModel):
    next: Optional[str] = None

    if TYPE_CHECKING:
        data: List[Any]


class Playlist(BaseModel):
    id: str
    title: str


class PlaylistsResponse(PaginatedResponse):
    data: List[Playlist]


class Album(BaseModel):
    id: int
    title: str

    def __str__(self) -> str:
        return self.title


class Artist(BaseModel):
    id: int
    name: str

    def __str__(self) -> str:
        return self.name


class Track(BaseModel):
    id: int
    title: str
    time_add: int
    album: Album
    artist: Artist

    def __str__(self) -> str:
        return f'{self.artist} - {self.title} ({self.album}) [added: {datetime.fromtimestamp(self.time_add)}]'


class PlaylistTracks(PaginatedResponse):
    data: List[Track]
