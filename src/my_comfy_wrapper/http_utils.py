from __future__ import annotations

import json
from urllib import parse, request


def http_get_json(url: str) -> dict:
    req = request.Request(url, method='GET')
    with request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))


def http_post_json(url: str, payload: dict) -> dict:
    data = json.dumps(payload).encode('utf-8')
    req = request.Request(url, data=data, headers={'Content-Type': 'application/json'}, method='POST')
    with request.urlopen(req, timeout=60) as resp:
        return json.loads(resp.read().decode('utf-8'))


def http_get_bytes(url: str, params: dict[str, str]) -> bytes:
    query = parse.urlencode(params)
    full_url = f"{url}?{query}"
    req = request.Request(full_url, method='GET')
    with request.urlopen(req, timeout=120) as resp:
        return resp.read()
