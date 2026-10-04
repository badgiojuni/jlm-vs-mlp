"""Appel LLM (OpenRouter) + boucle de traitement communes aux étapes 2 (filtre) et 3 (check)."""

import json
import logging
import sys
from collections.abc import Callable
from pathlib import Path
from urllib.error import HTTPError

from pipeline.http import fetch_json

log = logging.getLogger("llm")

OPENROUTER = "https://openrouter.ai/api/v1/chat/completions"
spent = 0.0  # $ dépensés depuis le lancement du process, appels en erreur compris


def chat(model: str, api_key: str, system: str, user: str, **extra) -> dict:
    """Renvoie le message de l'assistant. extra : response_format, tools, provider…"""
    global spent
    body = {
        "model": model,
        "temperature": 0,
        "messages": [{"role": "system", "content": system}, {"role": "user", "content": user}],
        "usage": {"include": True},
        **extra,
    }
    r = fetch_json(OPENROUTER, api_key, body)
    spent += r.get("usage", {}).get("cost", 0.0)  # compté AVANT validation : payé quand même
    choice = r["choices"][0]
    if not choice["message"].get(
        "content"
    ):  # rare avec Sonnet + recherche ; retenté au run suivant
        log.warning("réponse vide, finish_reason=%s", choice.get("finish_reason"))
    return choice["message"]


def read_jsonl(path: Path) -> list[dict]:
    return [json.loads(line) for line in path.read_text().splitlines()] if path.exists() else []


def run(todo: list[tuple[str, object]], process: Callable, out: Path, max_cost: float) -> None:
    """todo = [(id lisible, élément)]. Écrit chaque ligne dès qu'elle est prête,
    coupe-circuit budgétaire, code de sortie 1 si au moins une erreur (le job planifié apparaît en rouge)."""
    start, errors, n = spent, 0, 0
    with out.open("a") as f:
        for key, item in todo:
            if spent - start >= max_cost:
                log.warning("coupe-circuit : %.3f $ atteints, arrêt du run", spent - start)
                break
            try:
                row = process(item)
            except (ValueError, KeyError, HTTPError) as e:  # sortie invalide ou refus : on log
                log.error("%s : %s", key, e)
                errors += 1
                continue
            n += 1
            f.write(json.dumps(row, ensure_ascii=False) + "\n")
            f.flush()  # chaque ligne est acquise, même si le run plante après
    log.info("%d lignes écrites, %d erreurs, coût %.4f $", n, errors, spent - start)
    sys.exit(1 if errors else 0)
