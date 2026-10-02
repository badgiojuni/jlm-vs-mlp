from pipeline.eval_filter import score
from pipeline.filter import tweet_text


def test_retweet_uses_full_original_text_and_author():
    rec = {
        "tweet": {
            "id": "2",
            "text": "RT @J_Bardella: début tronqué…",
            "referenced_tweets": [{"type": "retweeted", "id": "1"}],
        },
        "referenced": [{"id": "1", "text": "court", "note_tweet": {"text": "texte long complet"}}],
    }
    assert tweet_text(rec) == "Retweet de @J_Bardella : texte long complet"


def test_quote_appends_quoted_tweet():
    rec = {
        "tweet": {
            "id": "2",
            "text": "Mon avis",
            "referenced_tweets": [{"type": "quoted", "id": "1"}],
        },
        "referenced": [{"id": "1", "text": "120 M€ annoncés"}],
    }
    assert tweet_text(rec) == "Mon avis\n\n[Tweet cité] 120 M€ annoncés"


def test_score():
    s = score([(True, True), (True, False), (False, True), (False, False)])
    assert s == {"accuracy": 0.5, "precision": 0.5, "recall": 0.5}
