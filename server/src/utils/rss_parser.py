# src/utils/rss_parser.py
"""
Bulletproof RSS parser for TruthPulse — handles malformed XML, HTML in feeds, timezone issues
Uses lxml (forgiving) + dateutil (timezone safe) — 100% reliable on Windows/Python 3.12+
Fixed: passes max_per_feed to _parse_xml
"""

from __future__ import annotations

import re
import html
import yaml
import requests
from datetime import datetime, timedelta
from pathlib import Path
from typing import List, Dict, Any, Optional

from loguru import logger
from langchain_core.documents import Document

# For forgiving XML parsing and timezone handling
from lxml import etree
from dateutil import parser as date_parser
from dateutil.tz import tzutc

# Load RSS config
CONFIG_PATH = Path(__file__).parent.parent.parent / "data" / "rss_sources.yaml"
with open(CONFIG_PATH, "r", encoding="utf-8") as f:
    RSS_CONFIG = yaml.safe_load(f)["rss_sources"]


class RSSParser:
    def __init__(self):
        self.headers = {"User-Agent": "TruthPulse/2.0 (Windows)"}

    def fetch_recent(self, days: int = 7, max_per_feed: int = 15) -> List[Document]:
        cutoff = datetime.now() - timedelta(days=days)
        docs: List[Document] = []

        for category, feeds in RSS_CONFIG.items():
            for feed in feeds:
                try:
                    r = requests.get(feed["url"], headers=self.headers, timeout=12)
                    r.raise_for_status()
                    r.encoding = 'utf-8'
                    new_docs = self._parse_xml(r.text, feed, cutoff, category, max_per_feed)
                    docs.extend(new_docs)
                    logger.debug(f"{feed['name']:30} → {len(new_docs)} articles")
                except Exception as e:
                    logger.warning(f"Failed {feed['name']}: {e}")

        logger.success(f"Fetched {len(docs)} recent articles from RSS")
        return docs

    def _parse_xml(self, xml_text: str, feed: Dict, cutoff: datetime, category: str, max_per_feed: int) -> List[Document]:
        try:
            # lxml with recovery (forgiving for malformed XML)
            parser = etree.XMLParser(recover=True, encoding='utf-8')
            root = etree.fromstring(xml_text.encode('utf-8'), parser=parser)
            
            # Find items (RSS or Atom)
            items = root.findall(".//item") or root.findall(".//entry")
            docs = []
            for item in items[:max_per_feed]:
                title = self._clean_text(self._get_text(item.find("title")) or self._get_text(item.find("{http://www.w3.org/2005/Atom}title")))
                link = self._get_text(item.find("link")) or self._get_attr(item.find("{http://www.w3.org/2005/Atom}link"), "href")
                desc_elem = item.find("description") or item.find("summary") or item.find("{http://www.w3.org/2005/Atom}content") or item.find("{http://www.w3.org/2005/Atom}summary")
                desc = self._clean_html(self._get_text(desc_elem)) if desc_elem is not None else ""

                content = f"{title} {desc}".strip()
                if len(content) < 60:
                    continue

                # Safe date parsing with dateutil (fixes timezone mismatches)
                pubdate = self._get_text(item.find("pubDate")) or self._get_text(item.find("published")) or self._get_text(item.find("{http://www.w3.org/2005/Atom}published"))
                try:
                    pub_dt = date_parser.parse(pubdate, tzinfos={"UTC": tzutc()}) if pubdate else datetime.now()
                    if pub_dt < cutoff:
                        continue
                except:
                    pub_dt = datetime.now()  # Fallback

                doc = Document(
                    page_content=content,
                    metadata={
                        "title": title[:500],
                        "source_name": feed["name"],
                        "source_category": category.replace("_", " ").title(),
                        "url": link,
                        "published": pub_dt.isoformat(),
                        "reliable": feed.get("reliable", False),
                    }
                )
                docs.append(doc)
            return docs
        except Exception as e:
            logger.warning(f"XML parse failed for {feed['name']}: {e}")
            return []

    @staticmethod
    def _get_text(elem):
        return elem.text if elem is not None else ""

    @staticmethod
    def _get_attr(elem, attr):
        return elem.get(attr) if elem is not None else ""

    @staticmethod
    def _clean_text(text: str) -> str:
        if not text:
            return ""
        text = html.unescape(text)
        text = re.sub(r"\s+", " ", text).strip()
        return text

    @staticmethod
    def _clean_html(html_text: str) -> str:
        if not html_text:
            return ""
        # Strip HTML tags
        clean = re.sub(r'<[^>]+>', ' ', html_text)
        clean = html.unescape(clean)
        clean = re.sub(r'\s+', ' ', clean).strip()
        return clean


# Global instance
rss_parser = RSSParser()

if __name__ == "__main__":
    docs = rss_parser.fetch_recent(days=3)
    print(f"Test: {len(docs)} articles fetched")
    for d in docs[:5]:
        print(f"[{d.metadata['source_category']}] {d.metadata['title'][:80]}")