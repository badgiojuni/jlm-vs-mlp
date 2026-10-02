"""Appel HTTP JSON avec retry + backoff, partagé par toutes les étapes du pipeline."""

import json
import logging
import time
import urllib.error
import urllib.request

log = logging.getLogger("http")


def fetch_json(url: str, token: str, body: dict | None = None, retries: int = 4) -> dict:
    """GET (ou POST si body) ; retry sur 429 / 5xx / erreur réseau, échec immédiat sinon."""
    data = json.dumps(body).encode() if body is not None else None
    headers = {"Authorization": f"Bearer {token}", "Content-Type": "application/json"}
    req = urllib.request.Request(url, data=data, headers=headers)
    where = url.split("?")[0]
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=120) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if (e.code != 429 and e.code < 500) or attempt == retries - 1:
                log.error("HTTP %s sur %s : %s", e.code, where, e.read().decode()[:500])
                raise
            reset = e.headers.get("x-rate-limit-reset")
            wait = int(reset) - time.time() if e.code == 429 and reset else 5 * 2**attempt
        except urllib.error.URLError as e:
            if attempt == retries - 1:
                raise
            log.warning("réseau : %s", e.reason)
            wait = 5 * 2**attempt
        wait = min(max(wait, 1), 900)
        log.warning("retry %d/%d dans %ds (%s)", attempt + 1, retries - 1, wait, where)
        time.sleep(wait)
    raise AssertionError("unreachable")
