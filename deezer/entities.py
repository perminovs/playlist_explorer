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


class Artist(BaseModel):
    id: int
    name: str


class Track(BaseModel):
    id: int
    title: str
    time_add: int
    album: Album
    artist: Artist


class TrackList(BaseModel):
    data: List[Track]


class PlaylistDetail(BaseModel):
    tracks: TrackList
