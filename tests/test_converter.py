import json
from datetime import datetime

from tekore._model import PlaylistTrack as SpotifyTrack

from playlist_organizer.client.base import Platform, Track
from playlist_organizer.client.deezer.entities import Album, Artist
from playlist_organizer.client.deezer.entities import Track as DeezerTrack


def test_track_convert_from_deezer():
    deezer_track = DeezerTrack(
        id=111,
        title='kek',
        time_add=1599377243,
        album=Album(id=222, title='Lol'),
        artist=Artist(id=333, name='Cheburek'),
    )
    track = Track.from_deezer(deezer_track)

    assert track.title == deezer_track.title
    assert track.artists == [deezer_track.artist.name]
    assert track.album == deezer_track.album.title
    assert track.external_id == str(deezer_track.id)
    assert track.source == Platform.DEEZER


def test_track_convert_from_spotify(raw_data_dir):
    with (raw_data_dir / 'spotify_track.json').open() as f:
        spotify_track = SpotifyTrack(**json.load(f))

    track = Track.from_spotify(spotify_track)
    assert track.title
    assert track.artists
    assert track.album
    assert track.added_at
    assert track.external_id == spotify_track.track.uri
    assert track.source is Platform.SPOTIFY
