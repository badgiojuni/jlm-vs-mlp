import json

from pipeline import ingest


def test_load_existing_gives_last_id_per_account(tmp_path):
    raw = tmp_path / "tweets.jsonl"
    rows = [("A", "9"), ("A", "10"), ("B", "5")]  # "10" > "9" en entier, pas en texte
    raw.write_text("".join(json.dumps({"account": a, "tweet": {"id": i}}) + "\n" for a, i in rows))
    seen, last = ingest.load_existing(raw)
    assert seen == {"9", "10", "5"}
    assert last == {"A": "10", "B": "5"}


def test_fetch_paginates_and_attaches_retweeted_text(monkeypatch):
    pages = [
        {
            "data": [{"id": "2", "text": "RT @x: tronqué…", "referenced_tweets": [{"id": "1"}]}],
            "includes": {"tweets": [{"id": "1", "text": "texte complet"}]},
            "meta": {"next_token": "p2"},
        },
        {"data": [{"id": "3", "text": "tweet"}], "meta": {}},
    ]
    calls = []
    monkeypatch.setattr(
        ingest,
        "get",
        lambda path, params, token: calls.append(dict(params)) or pages[len(calls) - 1],
    )

    out = ingest.fetch("A", "42", None, "tok")

    assert [r["tweet"]["id"] for r in out] == ["2", "3"]
    assert out[0]["referenced"] == [{"id": "1", "text": "texte complet"}]
    assert calls[0]["start_time"] == ingest.START_TIME  # 1er run : borne de départ
    assert calls[1]["pagination_token"] == "p2"
