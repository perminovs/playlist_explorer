from typing import List

import typer
from colorclass import Color
from terminaltables import AsciiTable

from playlist_organizer.client.base import Track
from playlist_organizer.matcher import MatchResult

MAX_LEN = 93


def _c(text: str, color: str) -> str:
    return Color(f'{{{color}}}{text}{{/{color}}}')


def render_matches(match_result: MatchResult) -> None:
    table_headers = [[_c('Deezer', color='automagenta'), _c('Spotify', color='automagenta')]]
    table_body = [[d.to_brief_str(MAX_LEN), s.to_brief_str(MAX_LEN)] for d, s in match_result.found.items()]
    found = AsciiTable(table_headers + table_body)
    typer.secho(found.table)

    _render_single('Deezer only', match_result.only_left)
    _render_single('Spotify only', match_result.only_right)


def _render_single(title: str, tracks: List[Track]) -> None:
    header = [[_c(title, color='automagenta')]]
    body = [[t.to_brief_str(MAX_LEN * 2)] for t in tracks]

    data = AsciiTable(header + body)
    typer.secho(data.table)
