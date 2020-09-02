import json


def pprint_resp(resp):
    print(json.dumps(resp.json(), ensure_ascii=False, indent=4, sort_keys=True))
