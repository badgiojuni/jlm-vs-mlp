import pytest

from pipeline.check import validate


def msg(content, urls=()):
    ann = [{"type": "url_citation", "url_citation": {"url": u}} for u in urls]
    return {"content": content, "annotations": ann}


def test_invented_url_is_dropped_and_fences_tolerated():
    content = '```json\n{"verdict": "vrai", "explanation": "ok", "sources": ["https://a.fr/", "https://invente.fr"]}\n```'
    assert validate(msg(content, ["https://a.fr"]))["sources"] == ["https://a.fr/"]


def test_verdict_without_real_source_is_rejected():
    content = '{"verdict": "faux", "explanation": "x", "sources": ["https://invente.fr"]}'
    with pytest.raises(ValueError):
        validate(msg(content))


def test_unverifiable_needs_no_source():
    content = '{"verdict": "invérifiable", "explanation": "opinion", "sources": []}'
    assert validate(msg(content))["verdict"] == "invérifiable"


def test_unknown_verdict_is_rejected():
    with pytest.raises(ValueError):
        validate(msg('{"verdict": "confirmé", "explanation": "x", "sources": []}'))
