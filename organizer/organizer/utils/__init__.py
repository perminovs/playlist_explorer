from __future__ import annotations

import json
import logging
from typing import Any, Dict, Generic, List, Type, TypeVar

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


class Stack(Generic[T]):
    def __init__(self) -> None:
        self._stack: List[T] = []

    def pop(self) -> T:
        return self._stack.pop()

    def push(self, value: T) -> None:
        self._stack.append(value)

    def is_empty(self) -> bool:
        return not bool(self._stack)
