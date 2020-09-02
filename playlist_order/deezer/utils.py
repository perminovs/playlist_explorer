import json
import logging

logger = logging.getLogger(__name__)


def pprint_resp(resp):
    logger.info('\n%s', json.dumps(resp.json(), ensure_ascii=False, indent=4, sort_keys=True))
