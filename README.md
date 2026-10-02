# JLM vs MLP — duel de crédibilité

Dashboard public : les tweets (et retweets) de Jean-Luc Mélenchon et Marine Le Pen,
filtrés puis fact-checkés par une IA avec recherche web, en vue de 2027.

## Architecture

```
GitHub Actions (cron)
  ingest → filter (affirmation factuelle ?) → check (LLM + web search) → build → GitHub Pages
```

Pas de serveur ni de base de données : les données sont versionnées dans `data/`.

## Démarrer en local

```bash
cp .env.example .env          # puis remplir les clés — .env n'est jamais commité
uv sync
uvx pre-commit install        # hooks : ruff + gitleaks avant chaque commit
```

## Lancer le pipeline

```bash
uv run --env-file .env python -m pipeline.ingest        # 1. nouveaux tweets → data/raw/
uv run --env-file .env python -m pipeline.filter        # 2. vérifiable ? → data/claims.jsonl
uv run --env-file .env python -m pipeline.eval_filter <modèles…>  # comparer des modèles
```
