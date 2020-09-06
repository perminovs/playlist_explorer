from unittest.mock import PropertyMock
from uuid import uuid4

import pytest
from pytest_httpx import HTTPXMock

from playlist_organizer.client.spotify.client import SpotifyClient
from playlist_organizer.client.spotify.settings import SpotifySettings


@pytest.fixture()
def settings():
    return SpotifySettings(api_host='https://dummy')


@pytest.fixture()
def client(settings, authenticator, mocker):
    spotify_client = SpotifyClient(settings=settings, authenticator=authenticator)

    user = mocker.MagicMock()
    user.id = '12312eqasds2'
    type(spotify_client)._current_user = PropertyMock(return_value=user)
    return spotify_client


@pytest.mark.parametrize(
    'response_filenames',
    [('spotify_playlists_1.json', 'spotify_playlists_2.json')],
    indirect=True,
)
def test_get_playlist_list(client, responses: HTTPXMock, json_responses):
    playlists = client.get_playlist_list()

    assert len(playlists) == 4
    assert {p.name for p in playlists} == {'playlist1', 'playlist2', 'playlist3', 'playlist4'}


@pytest.mark.parametrize(
    'response_filenames',
    [('spotify_playlists_1.json', 'spotify_playlists_2.json')],
    indirect=True,
)
def test_get_playlist_names(client, responses):
    assert client.get_playlist_names() == ['playlist1', 'playlist2', 'playlist3', 'playlist4']


@pytest.mark.parametrize(
    'response_filenames',
    [('spotify_playlists_1.json', 'spotify_playlists_2.json')],
    indirect=True,
)
def test_playlist_id_by_name(client, responses, response_filenames):
    assert client._playlist_id_by_name('playlist1') == 'playlist1_id'


@pytest.mark.parametrize(
    'response_filenames',
    [('spotify_playlist_tracks_1.json', 'spotify_playlist_tracks_2.json')],
    indirect=True,
)
def test_get_playlist_tracks(client, responses: HTTPXMock, mocker, json_responses):
    playlist_id = '5432'
    playlist_name = str(uuid4())

    client._playlist_id_by_name = mocker.MagicMock()
    client._playlist_id_by_name.return_value = playlist_id

    tracks = client.get_playlist_tracks(playlist_name)

    client._playlist_id_by_name.assert_called_once_with(playlist_name)

    assert len(tracks) == 4
    expected_titles = {'Маленький', 'Прыгаю-стою', 'Black Sheep', 'Caravane'}
    assert {t.title for t in tracks} == expected_titles
