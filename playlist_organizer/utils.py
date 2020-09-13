from __future__ import annotations

import datetime
import json
import logging
from json import JSONEncoder
from typing import Any, Dict, Generic, List, Optional, Type, TypeVar

import typer
from pydantic import ValidationError

logger = logging.getLogger(__name__)
T = TypeVar('T')


def pprint_json(resp: Dict[str, Any], fg: str = 'white') -> None:
    typer.secho(json.dumps(resp, ensure_ascii=False, indent=4, sort_keys=True), fg=fg)


def create_settings(settings_cls: Type[T], env_file: str) -> T:
    try:
        settings = settings_cls()
        logger.debug('Got settings %s without .env file', settings_cls)
    except ValidationError:
        settings = settings_cls(_env_file=env_file)  # type: ignore
        logger.debug('Got settings %s from .env file', settings_cls)
    return settings  # noqa R504


class Stack(Generic[T]):
    def __init__(self) -> None:
        self._stack: List[T] = []

    def pop(self) -> T:
        return self._stack.pop()

    def push(self, value: T) -> None:
        self._stack.append(value)

    def is_empty(self) -> bool:
        return not bool(self._stack)


class DateTimeEncoder(JSONEncoder):
    def default(self, o: Any) -> Optional[str]:
        if isinstance(o, (datetime.date, datetime.datetime)):
            return o.isoformat()
        return None
