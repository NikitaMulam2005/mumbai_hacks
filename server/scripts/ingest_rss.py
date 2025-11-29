#!/usr/bin/env python
"""
ingest_rss.py – Daily RSS ingestion for TruthPulse
Works perfectly with FAISS (no Chroma needed)
Automatically saves updated index to disk after ingestion
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from src.utils.rss_parser import rss_parser
from src.rag.vectorstore.vectorstore_manager import vectorstore_manager


def main():
    # Logging
    log_file = project_root / "logs" / "ingest_rss.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    logger.remove()
    logger.add(log_file, rotation="10 MB", retention="30 days")
    logger.add(sys.stderr, level="INFO")

    logger.info("=" * 60)
    logger.info("TRUTH PULSE RSS INGESTION STARTED")
    logger.info(f"Backend: {vectorstore_manager.active_backend.upper()}")
    logger.info(f"Current docs: {vectorstore_manager.count():,}")
    logger.info("=" * 60)

    # Fetch all recent articles (new parser gets everything)
    logger.info("Fetching latest articles from all sources...")
    new_docs = rss_parser.fetch_recent(days=5, max_per_feed=12)

    if not new_docs:
        logger.warning("No new articles found today")
        return

    # Deduplicate by URL
    seen_urls = {doc.metadata.get("url", "") for doc in vectorstore_manager.vectorstore.docstore._dict.values()}
    unique_new = []
    for doc in new_docs:
        url = doc.metadata.get("url", "").strip()
        if url and url not in seen_urls:
            seen_urls.add(url)
            unique_new.append(doc)

    if not unique_new:
        logger.info("All articles already in knowledge base")
        return

    logger.info(f"Adding {len(unique_new)} new articles to FAISS...")
    vectorstore_manager.add_documents(unique_new)

    # CRITICAL: Save updated FAISS to disk
    logger.info("Saving updated FAISS index to disk...")
    vectorstore_manager.save_to_faiss(path="vectorstore/faiss")

    logger.success(f"INGESTION COMPLETE — {len(unique_new)} new articles added")
    logger.success(f"Total knowledge base: {vectorstore_manager.count():,} chunks")
    logger.success("FAISS index saved to disk — ready for tomorrow!")
    logger.info("=" * 60)


if __name__ == "__main__":
    main()