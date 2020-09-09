from datetime import datetime

import pytest

from playlist_organizer.client.base import Platform, Track


def _create_track(title: str):
    return Track(
        artists=[''],
        album='',
        title=title,
        added_at=datetime.now(),
        source=Platform.DEEZER,
        external_id='',
    )


@pytest.mark.parametrize(
    ('title1', 'title2'),
    [
        # ('LOL', 'lol'),
        ('Kek - Live', 'Kek (live)'),
        ('Kek - Lol (feat. Cheburek)', 'kek - lol feat Cheburek'),
        ('Kek 142', 'Kek 142'),
        ('Kek 142.', 'Kek 142'),
    ],
)
def test_match_found(matcher, title1, title2):
    track1, track2 = _create_track(title1), _create_track(title2)
    result = matcher.match([track1], [track2])
    assert result.found


@pytest.mark.parametrize(
    ('title1', 'title2'),
    [
        ('kek lol', 'kek'),
        ('kek 142', 'kek 666'),
    ],
)
def test_no_match(matcher, title1, title2):
    track1, track2 = _create_track(title1), _create_track(title2)
    result = matcher.match([track1], [track2])
    assert not result.found
