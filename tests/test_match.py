import json

import pytest

from playlist_organizer.client.base import Track
from playlist_organizer.matcher import TrackMatcher


@pytest.fixture()
def matcher():
    return TrackMatcher()


def _from_dump(path):
    with path.open() as f:
        tracks = json.load(f)
        return [Track.parse_obj(t) for t in tracks]


@pytest.fixture()
def left_tracks(raw_data_dir):
    return _from_dump(raw_data_dir / 'tracks_deezer.json')


@pytest.fixture()
def right_tracks(raw_data_dir):
    return _from_dump(raw_data_dir / 'tracks_spotify.json')


@pytest.fixture()
def expected_mapping(left_tracks, right_tracks):
    return {t1: t2 for t1, t2 in zip(left_tracks, right_tracks)}


def test_simple_match(matcher, left_tracks, right_tracks, expected_mapping):
    result = matcher.match(left_tracks, right_tracks)
    assert {t1: t2 for t1, t2 in result.found.items()} == expected_mapping
    assert not result.only_left
    assert not result.only_right


def test_shuffle_match(matcher, left_tracks, right_tracks, expected_mapping):
    left_tracks.append(left_tracks.pop(0))

    result = matcher.match(left_tracks, right_tracks)

    actual = {t1: t2 for t1, t2 in result.found.items()}
    assert actual == expected_mapping
    assert not result.only_left
    assert not result.only_right


@pytest.mark.parametrize('pop_index', [0, -1])
def test_match_lose_right(matcher, left_tracks, right_tracks, expected_mapping, pop_index):
    popped = right_tracks.pop(pop_index)
    expected = {t1: t2 for t1, t2 in expected_mapping.items() if t2 != popped}

    result = matcher.match(left_tracks, right_tracks)

    actual = {t1: t2 for t1, t2 in result.found.items()}
    assert actual == expected
    assert not result.only_right
    assert len(result.only_left) == 1
    assert result.only_left[0] == left_tracks[pop_index]


@pytest.mark.parametrize('pop_index', [0, -1])
def test_match_lose_left(matcher, left_tracks, right_tracks, expected_mapping, pop_index):
    popped = left_tracks.pop(pop_index)
    expected = {t1: t2 for t1, t2 in expected_mapping.items() if t1 != popped}

    result = matcher.match(left_tracks, right_tracks)

    actual = {t1: t2 for t1, t2 in result.found.items()}
    assert actual == expected
    assert not result.only_left
    assert len(result.only_right) == 1
    assert result.only_right[0] == right_tracks[pop_index]
