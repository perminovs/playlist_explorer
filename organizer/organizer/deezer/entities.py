from datetime import datetime
from typing import List

from pydantic import BaseModel


class Playlist(BaseModel):
    id: int
    title: str


class PlaylistsResponse(BaseModel):
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


class TrackList(BaseModel):
    data: List[Track]


class PlaylistDetail(BaseModel):
    tracks: TrackList
