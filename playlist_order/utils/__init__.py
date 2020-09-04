from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from typing import Any, Callable, Dict, List, Type, TypeVar, Union

import typer
from pydantic import ValidationError

logger = logging.getLogger(__name__)
T = TypeVar('T')


def pprint_json(resp: Dict[str, Any]) -> None:
    typer.secho(json.dumps(resp, ensure_ascii=False, indent=4, sort_keys=True), fg='white')


def create_settings(settings_cls: Type[T], env_file: str) -> T:
    try:
        settings = settings_cls()
        logger.debug('Got settings %s without .env file', settings_cls)
    except ValidationError:
        settings = settings_cls(_env_file=env_file)  # type: ignore
        logger.debug('Got settings %s from .env file', settings_cls)
    return settings  # noqa R504


class Stack:
    def __init__(self) -> None:
        self._stack: List[Any] = []

    def pop(self) -> Any:
        return self._stack.pop()

    def push(self, value: Any) -> None:
        self._stack.append(value)

    def is_empty(self) -> bool:
        return not bool(self._stack)


MenuAction = Callable[[], Any]


@dataclass
class MenuItem:
    title: str
    choices: Dict[str, Union[MenuAction, MenuItem]]
