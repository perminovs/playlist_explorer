import json

import pytest

from playlist_organizer.client.auth.base import Token

VALID_TOKEN = {
    "expire_time": "2020-09-08T23:46:03.820645",
    "value": "lol-kek",
}


def test_load_token(tmp_path):
    path = tmp_path / 'kek.json'
    with path.open('w') as f:
        json.dump(VALID_TOKEN, f)

    token = Token.load(path)
    assert token
    assert token.value == VALID_TOKEN['value']


def test_save_and_load(tmp_path):
    path = tmp_path / 'kek.json'
    Token(**VALID_TOKEN).dump(path)

    assert Token.load(path).value == VALID_TOKEN['value']


def test_load_from_not_exists_file(tmp_path):
    assert Token.load(tmp_path / 'lol.json') is None


@pytest.mark.parametrize('content', ['"valid json"', 'lol 123asd [as d1sas kek'])
def test_load_from_invalid_format(tmp_path, content):
    path = tmp_path / 'kek.json'
    with path.open('w') as f:
        json.dump(content, f)

    assert Token.load(path) is None
    assert not path.exists()
