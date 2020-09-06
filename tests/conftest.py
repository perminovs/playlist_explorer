import pathlib

import pytest


@pytest.fixture()
def raw_data_dir():
    return pathlib.Path(__file__).parent / 'raw_responses'
