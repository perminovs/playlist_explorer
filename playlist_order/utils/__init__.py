import json
import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def pprint_resp(resp: Dict[str, Any]) -> None:
    logger.info('\n%s', json.dumps(resp, ensure_ascii=False, indent=4, sort_keys=True))
