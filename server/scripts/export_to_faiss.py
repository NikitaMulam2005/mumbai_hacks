#!/usr/bin/env python
"""
export_to_faiss.py – Save current in-memory FAISS vectorstore to disk
Works in pure FAISS mode (no Chroma needed)
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

from loguru import logger
from src.rag.vectorstore.vectorstore_manager import vectorstore_manager


def main():
    logger.info("Saving current FAISS vectorstore to disk (vectorstore/faiss/)")

    if vectorstore_manager.active_backend != "faiss":
        logger.error(f"Current backend is {vectorstore_manager.active_backend} — cannot export")
        logger.error("You must be using FAISS to run this script")
        sys.exit(1)

    count = vectorstore_manager.count()
    if count == 0:
        logger.error("FAISS vectorstore is empty!")
        logger.error("Run: python scripts/prepare_vectorstore.py first")
        sys.exit(1)

    logger.info(f"Saving {count:,} documents to vectorstore/faiss/ ...")
    vectorstore_manager.save_to_faiss(path="vectorstore/faiss")

    logger.success("FAISS index saved permanently to disk!")
    logger.success("Next time you start, it will load in <2 seconds")
    logger.success("You are now production-ready!")


if __name__ == "__main__":
    main()