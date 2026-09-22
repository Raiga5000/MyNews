"""Collect candidate news items for each MyNews category into data/news.json.

This script only gathers candidates. How many of them actually reach the site,
and which ones, is decided later by the daily MyNews update task, which can
judge whether a story is big enough to be worth a slot.
"""
import html
import json
import re
import urllib.parse
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUTPUT = ROOT / "data" / "news.json"

JA = {"hl": "ja", "gl": "JP", "ceid": "JP:ja"}

# "limit" is how many CANDIDATES to collect, not how many are published.
CATEGORIES = {
    "it": {
        "label": "IT関連",
        "query": "IT OR AI OR テクノロジー",
        "limit": 10,
    },
    "security": {
        "label": "セキュリティ",
        "query": "セキュリティ インシデント OR 情報漏洩 OR 不正アクセス OR 脆弱性",
        "limit": 10,
    },
    "network": {
        "label": "通信技術",
        "query": "通信技術 OR 6G OR 5G OR 光通信 OR 衛星通信",
        "limit": 10,
    },
    "outing": {
        "label": "おでかけ",
        "query": "東京 おでかけスポット OR 神奈川 おでかけスポット OR 東京 新名所 OR 神奈川 新名所 OR 横浜 夜景",
        "limit": 12,
    },
    "jp": {
        # Google News' own Japanese top-stories feed, not a keyword search,
        # so the items are always current rather than evergreen listicles.
        "label": "日本のトップ",
        "feed": "https://news.google.com/rss?hl=ja&gl=JP&ceid=JP:ja",
        "limit": 12,
    },
    "world": {
        # English-language world section: stories that Japanese outlets
        # often do not carry. Titles get translated downstream.
        "label": "世界のトップ",
        "feed": "https://news.google.com/rss/headlines/section/topic/WORLD?hl=en-US&gl=US&ceid=US:en",
        "limit": 12,
    },
}


def clean(value):
    value = re.sub(r"<[^>]+>", "", value or "")
    return html.unescape(value).strip()


def feed_url(config):
    if "feed" in config:
        return config["feed"]
    params = urllib.parse.urlencode(dict(JA, q=config["query"]))
    return f"https://news.google.com/rss/search?{params}"


def fetch_category(category, config):
    request = urllib.request.Request(
        feed_url(config), headers={"User-Agent": "MyNews/1.0"}
    )
    with urllib.request.urlopen(request, timeout=30) as response:
        root = ET.fromstring(response.read())

    articles = []
    for rank, item in enumerate(root.findall("./channel/item")[: config["limit"]]):
        published = item.findtext("pubDate", "")
        date = None
        try:
            date = parsedate_to_datetime(published).astimezone(timezone.utc)
        except (TypeError, ValueError):
            pass
        articles.append({
            "id": f"{category}-{rank}",
            "category": category,
            "label": config["label"],
            "title": clean(item.findtext("title")),
            "url": item.findtext("link", "#"),
            "time": datetime.now().astimezone().strftime("%m/%d %H:%M"),
            "publishedAt": date.isoformat() if date else "",
            "score": max(60, 100 - rank * 4),
        })
    return articles


def main():
    all_articles = []
    errors = []
    for category, config in CATEGORIES.items():
        try:
            all_articles.extend(fetch_category(category, config))
        except Exception as error:  # One unavailable feed must not block the rest.
            errors.append(f"{category}: {error}")

    if not all_articles:
        raise RuntimeError("No news articles could be fetched: " + "; ".join(errors))

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(
        json.dumps(
            {"updatedAt": datetime.now(timezone.utc).isoformat(), "articles": all_articles},
            ensure_ascii=False,
            indent=2,
        ),
        encoding="utf-8",
    )
    print(f"Saved {len(all_articles)} candidate articles")
    if errors:
        print("Partial feed errors: " + "; ".join(errors))


if __name__ == "__main__":
    main()
