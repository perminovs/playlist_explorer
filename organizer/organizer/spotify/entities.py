from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class BasePaginatedResponse(BaseModel):
    next: Optional[str]


class Playlist(BaseModel):
    id: str
    title: str = Field(..., alias='name')


class PlaylistsAnswer(BasePaginatedResponse):
    items: List[Playlist]


class Artist(BaseModel):
    id: str
    name: str

    def __str__(self) -> str:
        return self.name


class Album(BaseModel):
    name: str
    artists: List[Artist]

    def __str__(self) -> str:
        return self.name


class Track(BaseModel):
    id: str
    name: str
    album: Album
    artists: List[Artist]

    def __str__(self) -> str:
        artists = '; '.join([str(a) for a in self.artists])
        return f'{artists} - {self.name} ({self.album})'


class TrackInfo(BaseModel):
    added_at: datetime
    track: Track

    def __str__(self) -> str:
        return f'{self.track} [added: {self.added_at}]'


class PlaylistDetail(BasePaginatedResponse):
    tracks: List[TrackInfo] = Field(..., alias='items')
