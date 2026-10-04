"""Compare des modèles sur le golden set du fact-check : justesse, erreurs graves, coût, latence.

Usage : uv run --env-file .env python -m pipeline.eval_check modele1 modele2 ...
Erreur grave = "vrai" <-> "faux" : publier l'inverse de la réalité est pire que tout le reste.
"""

import os
import sys
import time
from pathlib import Path

from pipeline import llm
from pipeline.check import check

GOLDEN = Path("data/golden/check.jsonl")


def main() -> None:
    key = os.environ["OPENROUTER_API_KEY"]
    golden = llm.read_jsonl(GOLDEN)
    print(f"{'modèle':40} {'justes':>6} {'graves':>6} {'invalides':>9} {'coût $':>8} {'s/aff':>6}")
    for model in sys.argv[1:]:
        ok = grave = invalid = 0
        start, t0 = llm.spent, time.time()
        for g in golden:
            try:
                pred = check(g["claim"], g["date"], "", model, key)["verdict"]
            except (ValueError, KeyError, OSError) as e:  # sortie invalide / HTTP = erreur comptée
                print(f"  ! {model} : {e}", file=sys.stderr)
                pred, invalid = None, invalid + 1
            ok += pred == g["verdict"]
            grave += {pred, g["verdict"]} == {"vrai", "faux"}
            if pred != g["verdict"]:
                print(
                    f"  ✗ {model} : {pred} au lieu de {g['verdict']} | {g['claim'][:70]!r}",
                    file=sys.stderr,
                )
        dt = (time.time() - t0) / len(golden)
        print(
            f"{model:40} {ok:>3}/{len(golden):<2} {grave:6} {invalid:9}"
            f" {llm.spent - start:8.4f} {dt:6.1f}"
        )


if __name__ == "__main__":
    main()
