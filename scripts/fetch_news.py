"""Fetch up to five Japanese news items for each MyNews category into data/news.json."""
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
CATEGORIES = {
    "it": ("IT関連", "IT OR AI OR テクノロジー", "JA"),
    "dq": ("ドラクエ", "ドラゴンクエスト OR ドラクエ", "JA"),
    "festival": ("関東の夏祭り", "関東 夏祭り OR 花火大会", "JA"),
    "yokohama": ("横浜イベント", "横浜 イベント", "JA"),
    "top": ("トップニュース", "日本 海外 主要ニュース", "JA"),
}

def clean(value):
    value = re.sub(r"<[^>]+>", "", value or "")
    return html.unescape(value).strip()

def fetch_category(category, label, query, country):
    params = urllib.parse.urlencode({"q": query, "hl": "ja", "gl": "JP", "ceid": "JP:ja"})
    request = urllib.request.Request(f"https://news.google.com/rss/search?{params}", headers={"User-Agent": "MyNews/1.0"})
    with urllib.request.urlopen(request, timeout=30) as response:
        root = ET.fromstring(response.read())
    articles = []
    for rank, item in enumerate(root.findall("./channel/item")[:5]):
        published = item.findtext("pubDate", "")
        try:
            date = parsedate_to_datetime(published).astimezone(timezone.utc)
            time_text = date.astimezone().strftime("%m/%d %H:%M")
        except (TypeError, ValueError):
            time_text = published
        articles.append({
            "id": f"{category}-{rank}", "category": category, "label": label,
            "title": clean(item.findtext("title")), "summary": clean(item.findtext("description")),
            "url": item.findtext("link", "#"), "time": time_text, "score": max(60, 100 - rank * 7),
        })
    return articles

def main():
    all_articles = []
    errors = []
    for category, (label, query, country) in CATEGORIES.items():
        try:
            all_articles.extend(fetch_category(category, label, query, country))
        except Exception as error:  # One unavailable feed should not block other categories.
            errors.append(f"{category}: {error}")
    if not all_articles:
        raise RuntimeError("No news articles could be fetched: " + "; ".join(errors))
    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(json.dumps({"updatedAt": datetime.now(timezone.utc).isoformat(), "articles": all_articles}, ensure_ascii=False, indent=2), encoding="utf-8")
    print(f"Saved {len(all_articles)} articles")
    if errors:
        print("Partial feed errors: " + "; ".join(errors))

if __name__ == "__main__":
    main()
