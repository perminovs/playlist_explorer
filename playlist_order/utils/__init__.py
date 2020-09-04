import json
import logging
from typing import Any, Dict, Type, TypeVar

from pydantic import ValidationError

logger = logging.getLogger(__name__)
T = TypeVar('T')


def pprint_json(resp: Dict[str, Any]) -> None:
    logger.info('\n%s', json.dumps(resp, ensure_ascii=False, indent=4, sort_keys=True))


def create_settings(settings_cls: Type[T], env_file: str) -> T:
    try:
        settings = settings_cls()
        logger.debug('Got settings %s without .env file', settings_cls)
    except ValidationError:
        settings = settings_cls(_env_file=env_file)  # type: ignore
        logger.debug('Got settings %s from .env file', settings_cls)
    return settings  # noqa R504
