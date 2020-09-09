import pytest

from playlist_organizer.matcher import TrackMatcher


@pytest.fixture()
def matcher():
    return TrackMatcher(match_threshold=0)
