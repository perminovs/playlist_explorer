import enum
import logging

import inquirer
import typer
from inquirer.render import ConsoleRender
from inquirer.themes import GreenPassion, term

from organizer.factory.clients import ClientFactory
from organizer.factory.menu import MenuItem, build_menu
from organizer.utils import Stack

app = typer.Typer()
logger = logging.getLogger(__name__)

theme = GreenPassion()
theme.List.unselected_color = term.yellow
render = ConsoleRender(theme=theme)


class LogLevel(str, enum.Enum):
    DEBUG = logging._levelToName[logging.DEBUG]
    INFO = logging._levelToName[logging.INFO]
    WARNING = logging._levelToName[logging.WARNING]
    ERROR = logging._levelToName[logging.ERROR]


@app.command()
def main(log_level: LogLevel = LogLevel.INFO) -> None:
    logging.basicConfig(level=log_level.value, format='%(asctime)s [%(levelname)s]: %(message)s')

    client_factory = ClientFactory()
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
            chosen()
        else:
            raise RuntimeError('Option not found')


if __name__ == '__main__':
    app()
