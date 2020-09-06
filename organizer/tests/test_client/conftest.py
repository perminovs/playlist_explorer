import json
from urllib.parse import parse_qs, urlparse

import pytest

from organizer.client.auth.base import BaseAuthenticator


def get_qs(url):
    return parse_qs(urlparse(url).query)


@pytest.fixture()
def authenticator(mocker):
    return mocker.create_autospec(BaseAuthenticator)


@pytest.fixture()
def response_filenames(request):
    return request.param


@pytest.fixture()
def json_responses(raw_data_dir, response_filenames):
    jsons = []
    for filename in response_filenames:
        with (raw_data_dir / filename).open() as f:
            jsons.append(json.load(f))
    return jsons


@pytest.fixture()
def responses(httpx_mock, json_responses):
    for response in json_responses:
        httpx_mock.add_response(json=response)
    return httpx_mock
