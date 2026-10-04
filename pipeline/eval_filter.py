"""Compare des modèles sur le golden set du filtre : qualité, coût, latence.

Usage : uv run --env-file .env python -m pipeline.eval_filter modele1 modele2 ...
Classe positive = "vérifiable". Le rappel compte le plus : un tweet factuel raté
ne sera jamais fact-checké, alors qu'un faux positif coûte juste un check inutile.
"""

import json
import os
import sys
import time
from pathlib import Path

from pipeline import llm
from pipeline.filter import classify, tweet_text

GOLDEN = Path("data/golden/filter.jsonl")


def score(pairs: list[tuple[bool, bool]]) -> dict:
    """pairs = [(attendu, prédit)] -> accuracy, précision, rappel."""
    tp = sum(a and p for a, p in pairs)
    fp = sum(p and not a for a, p in pairs)
    fn = sum(a and not p for a, p in pairs)
    return {
        "accuracy": sum(a == p for a, p in pairs) / len(pairs),
        "precision": tp / (tp + fp) if tp + fp else 0.0,
        "recall": tp / (tp + fn) if tp + fn else 0.0,
    }


def main() -> None:
    key = os.environ["OPENROUTER_API_KEY"]
    golden = [json.loads(line) for line in GOLDEN.read_text().splitlines()]
    print(f"{'modèle':40} {'acc':>5} {'préc':>5} {'rappel':>6} {'coût $':>8} {'s/tweet':>7}")
    for model in sys.argv[1:]:
        pairs, start, t0 = [], llm.spent, time.time()
        for g in golden:
            text = tweet_text(g["record"]) if "record" in g else g["text"]
            try:
                pred = classify(text, model, key)["verifiable"]
            except (ValueError, KeyError, OSError) as e:  # schéma cassé / HTTP = erreur comptée
                print(f"  ! {model} sur {g['source']} : {e}", file=sys.stderr)
                pred = not g["verifiable"]
            pairs.append((g["verifiable"], pred))
            if pred != g["verifiable"]:
                print(f"  ✗ {model} : attendu {g['verifiable']} | {text[:80]!r}", file=sys.stderr)
        s = score(pairs)
        dt = (time.time() - t0) / len(golden)
        print(
            f"{model:40} {s['accuracy']:5.2f} {s['precision']:5.2f} {s['recall']:6.2f}"
            f" {llm.spent - start:8.5f} {dt:7.1f}"
        )


if __name__ == "__main__":
    main()
