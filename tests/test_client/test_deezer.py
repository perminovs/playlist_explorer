from uuid import uuid4

import pytest
from pytest_httpx import HTTPXMock

from playlist_organizer.client.deezer.client import DeezerClient
from playlist_organizer.client.deezer.entities import Playlist
from playlist_organizer.client.deezer.settings import DeezerSettings
from tests.test_client.conftest import get_qs


@pytest.fixture()
def settings():
    return DeezerSettings(api_host='https://dummy')


@pytest.fixture()
def client(settings, authenticator):
    return DeezerClient(settings=settings, authenticator=authenticator)


@pytest.mark.parametrize(
    'response_filenames',
    [('deezer_playlists_1.json', 'deezer_playlists_2.json')],
    indirect=True,
)
def test_get_playlist_list(client, responses: HTTPXMock, json_responses):
    playlists = client.get_playlist_list()

    assert len(playlists) == 4
    assert {p.title for p in playlists} == {'playlist1', 'playlist2', 'playlist3', 'playlist4'}

    expected_qs = get_qs(json_responses[0]['next'])
    actual_qs = get_qs(str(responses.get_requests()[1].url))
    assert expected_qs['index'] == actual_qs['index']


@pytest.mark.parametrize(
    'response_filenames',
    [('deezer_playlists_1.json', 'deezer_playlists_2.json')],
    indirect=True,
)
def test_get_playlist_names(client, responses):
    assert client.get_playlist_names() == ['playlist1', 'playlist2', 'playlist3', 'playlist4']


def test_playlist_id_by_name(client, mocker):
    client.get_playlist_list = mocker.MagicMock()
    client.get_playlist_list.return_value = [Playlist(id='123', title='kek'), Playlist(id='312', title='lol')]
    assert client._playlist_id_by_name('lol') == '312'


@pytest.mark.parametrize(
    'response_filenames',
    [('deezer_playlist_tracks_1.json', 'deezer_playlist_tracks_2.json')],
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
    expected_titles = {'Highway Star', 'Pictures Of Home (Remastered 2012)', 'Burn (Remastered 2004)', 'Lazy'}
    assert {t.title for t in tracks} == expected_titles

    assert all(playlist_id in str(r.url) for r in responses.get_requests())

    expected_qs = get_qs(json_responses[0]['next'])
    actual_qs = get_qs(str(responses.get_requests()[1].url))
    assert expected_qs['index'] == actual_qs['index']
