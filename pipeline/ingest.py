"""Étape 1 : récupère les nouveaux tweets + retweets des deux candidats (API X v2).

Couche brute (bronze) : append-only dans data/raw/tweets.jsonl, objet API tel quel.
Idempotent : since_id = dernier tweet déjà stocké par compte, donc relancer ne crée
ni doublon ni relecture facturée.

Usage : uv run --env-file .env python -m pipeline.ingest
"""

import json
import logging
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from datetime import UTC, datetime
from pathlib import Path

log = logging.getLogger("ingest")

API = "https://api.x.com/2"
RAW = Path("data/raw/tweets.jsonl")
START_TIME = "2026-10-02T00:00:00Z"  # périmètre : rien avant le lancement du projet
COST_PER_POST = 0.005  # $ par post lu, tarif X pay-per-use (vérifié 2026-10)
# ponytail: IDs figés, un lookup coûte 0,01 $ et l'ID survit à un changement de pseudo
ACCOUNTS = {"JLMelenchon": "80820758", "MLP_officiel": "217749896"}
PARAMS = {
    "max_results": "100",
    "exclude": "replies",  # tweets + retweets (+ citations), pas les réponses
    "tweet.fields": "created_at,referenced_tweets,lang,public_metrics,note_tweet,entities",
    "expansions": "referenced_tweets.id",  # texte complet des tweets retweetés/cités
}


def get(path: str, params: dict, token: str, retries: int = 4) -> dict:
    """GET avec retry + backoff sur 429 / 5xx / erreur réseau."""
    url = f"{API}{path}?{urllib.parse.urlencode(params)}"
    req = urllib.request.Request(url, headers={"Authorization": f"Bearer {token}"})
    for attempt in range(retries):
        try:
            with urllib.request.urlopen(req, timeout=30) as r:
                return json.load(r)
        except urllib.error.HTTPError as e:
            if (e.code != 429 and e.code < 500) or attempt == retries - 1:
                log.error("HTTP %s sur %s : %s", e.code, path, e.read().decode()[:500])
                raise
            reset = e.headers.get("x-rate-limit-reset")
            wait = int(reset) - time.time() if e.code == 429 and reset else 5 * 2**attempt
        except urllib.error.URLError as e:
            if attempt == retries - 1:
                raise
            log.warning("réseau : %s", e.reason)
            wait = 5 * 2**attempt
        wait = min(max(wait, 1), 900)
        log.warning("retry %d/%d dans %ds", attempt + 1, retries - 1, wait)
        time.sleep(wait)
    raise AssertionError("unreachable")


def load_existing(path: Path) -> tuple[set[str], dict[str, str]]:
    """IDs déjà stockés + dernier ID par compte (l'état se déduit des données)."""
    seen, last = set(), {}
    if path.exists():
        for line in path.read_text().splitlines():
            rec = json.loads(line)
            tid, acc = rec["tweet"]["id"], rec["account"]
            seen.add(tid)
            if int(tid) > int(last.get(acc, 0)):
                last[acc] = tid
    return seen, last


def fetch(account: str, user_id: str, since_id: str | None, token: str) -> list[dict]:
    """Tous les nouveaux tweets d'un compte, toutes pages confondues."""
    params = dict(PARAMS, **({"since_id": since_id} if since_id else {"start_time": START_TIME}))
    out = []
    while True:
        page = get(f"/users/{user_id}/tweets", params, token)
        refs = {t["id"]: t for t in page.get("includes", {}).get("tweets", [])}
        for t in page.get("data", []):
            linked = [refs[r["id"]] for r in t.get("referenced_tweets", []) if r["id"] in refs]
            out.append({"account": account, "tweet": t, "referenced": linked})
        if not (nxt := page.get("meta", {}).get("next_token")):
            return out
        params["pagination_token"] = nxt


def main() -> None:
    logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
    token = os.environ["X_BEARER_TOKEN"]
    seen, last = load_existing(RAW)
    RAW.parent.mkdir(parents=True, exist_ok=True)
    now = datetime.now(UTC).isoformat(timespec="seconds")
    reads = new = 0
    for account, user_id in ACCOUNTS.items():
        recs = fetch(account, user_id, last.get(account), token)
        reads += sum(1 + len(r["referenced"]) for r in recs)
        fresh = [r for r in recs if r["tweet"]["id"] not in seen]
        # Écrit après fetch complet, du plus ancien au plus récent : un crash en cours de
        # route ne peut pas faire avancer since_id au-delà de tweets non encore stockés.
        fresh.sort(key=lambda r: int(r["tweet"]["id"]))
        with RAW.open("a") as f:
            for r in fresh:
                f.write(json.dumps({**r, "fetched_at": now}, ensure_ascii=False) + "\n")
        seen.update(r["tweet"]["id"] for r in fresh)
        new += len(fresh)
        log.info("%s : %d nouveaux tweets", account, len(fresh))
    log.info(
        "total %d nouveaux, %d posts lus, coût estimé %.3f $", new, reads, reads * COST_PER_POST
    )


if __name__ == "__main__":
    main()
