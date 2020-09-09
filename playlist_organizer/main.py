import enum
import logging

import inquirer
import typer
from inquirer.render import ConsoleRender
from inquirer.themes import GreenPassion, term

from playlist_organizer.menu.builder import MenuItem, build_menu
from playlist_organizer.menu.factory import Factory
from playlist_organizer.utils import Stack

app = typer.Typer()
logger = logging.getLogger(__name__)

theme = GreenPassion()
theme.List.unselected_color = term.yellow
render = ConsoleRender(theme=theme)


class LogLevel(str, enum.Enum):
    DEBUG = logging._levelToName[logging.DEBUG]  # pylint: disable=W0212
    INFO = logging._levelToName[logging.INFO]  # pylint: disable=W0212
    WARNING = logging._levelToName[logging.WARNING]  # pylint: disable=W0212
    ERROR = logging._levelToName[logging.ERROR]  # pylint: disable=W0212


@app.command()
def main(log_level: LogLevel = LogLevel.INFO) -> None:
    logging.basicConfig(level=log_level.value, format='%(asctime)s [%(levelname)s]: %(message)s')

    client_factory = Factory()
    top_level_menu = build_menu(client_factory)

    run_menu_loop(start_menu=top_level_menu)


def run_menu_loop(start_menu: MenuItem) -> None:
    _exit = 'EXIT'
    _back = 'BACK'

    current_menu = start_menu
    menu_history = Stack[MenuItem]()
    while True:
        additional_choices = [_exit] if menu_history.is_empty() else [_back, _exit]
        choices = list(current_menu.choices) + additional_choices  # type: ignore
        option = inquirer.list_input(message=current_menu.title, choices=choices, render=render)

        if not option or option == _exit:
            return

        if option == _back:
            current_menu = menu_history.pop()
            continue

        chosen = current_menu.choices[option]

        if isinstance(chosen, MenuItem):
            menu_history.push(current_menu)
            current_menu = chosen
        elif callable(chosen):
            try:
                chosen()
            except Exception:  # pylint: disable=W0703
                logger.exception('Something went wrong, try again')
        else:
            raise RuntimeError('Option not found')
