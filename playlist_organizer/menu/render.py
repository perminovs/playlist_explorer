from typing import List, TypeVar

import inquirer
import typer
from colorclass import Color
from terminaltables import AsciiTable

from playlist_organizer.client.base import Track
from playlist_organizer.matcher import MatchResult

T = TypeVar('T')
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
    if not tracks:
        return
    header = [[_c(title, color='automagenta')]]
    body = [[t.to_brief_str(MAX_LEN * 2)] for t in tracks]

    data = AsciiTable(header + body)
    typer.secho(data.table)


def choose_from_inquirer_list(title: str, items: List[T]) -> int:
    """Render inquirer.list_input with given <items> and return index of choosen item.

    Following call
    >>> choose_from_inquirer_list('kek', ['a', 'b', 'c'])
    will render:
    # kek:
    # > 1. a
    #   2. b
    #   3. c
    and return 0 after choosing first option.
    """
    last_idx = len(items)
    last_idx_len = len(str(last_idx))
    answer: str = inquirer.list_input(
        title,
        choices=[f'{str(idx).rjust(last_idx_len)}. {item}' for idx, item in enumerate(items, start=1)],
    )
    return int(answer[: answer.find('.')]) - 1  # no, I don't like regexps. Nobody likes
