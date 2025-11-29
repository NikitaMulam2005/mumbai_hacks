#!/usr/bin/env python
"""
prepare_vectorstore.py – Build historical fake/real news knowledge base
100% working on Windows + LangChain 0.3+ + FAISS
No Chroma, no C++ compiler, no errors
"""

import sys
from pathlib import Path

project_root = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(project_root))

import pandas as pd
from loguru import logger

from src.rag.vectorstore.vectorstore_manager import vectorstore_manager
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain_community.document_loaders import DataFrameLoader


DATA_DIR = project_root / "data"
RAW_FAKE = DATA_DIR / "Fake.csv"
RAW_TRUE = DATA_DIR / "True.csv"
COMBINED_CSV = DATA_DIR / "fake_news_dataset.csv"

CHUNK_SIZE = 800
CHUNK_OVERLAP = 100
SAMPLE_SIZE = 5000  # Remove this line later for full dataset


def main():
    logger.info("Building TruthPulse historical knowledge base")

    if not RAW_FAKE.exists() or not RAW_TRUE.exists():
        logger.error("Missing Fake.csv or True.csv!")
        logger.error("Download from: https://www.kaggle.com/clmentbisaillon/fake-and-real-news-dataset")
        sys.exit(1)

    logger.info("Loading datasets...")
    fake_df = pd.read_csv(RAW_FAKE)
    true_df = pd.read_csv(RAW_TRUE)
    logger.info(f"Loaded {len(fake_df):,} fake + {len(true_df):,} real articles")

    fake_df["label"] = "FAKE"
    true_df["label"] = "REAL"

    df = pd.concat([fake_df, true_df], ignore_index=True)
    df["text"] = df["title"].fillna("") + " " + df["text"].fillna("")
    df = df[df["text"].str.len() > 80]

    # Optional: use full dataset (comment out the next line for full power)
    df = df.sample(n=min(SAMPLE_SIZE, len(df)), random_state=42)

    df[["title", "text", "subject", "date", "label"]].to_csv(COMBINED_CSV, index=False)
    logger.success(f"Combined dataset saved → {COMBINED_CSV}")

    # Load documents (metadata_columns removed — fixed for LangChain 0.3+)
    loader = DataFrameLoader(df, page_content_column="text")
    docs = loader.load()

    # Manually attach metadata (required in newer LangChain)
    for i, doc in enumerate(docs):
        row = df.iloc[i]
        doc.metadata = {
            "title": str(row.get("title", "")),
            "label": row["label"],
            "subject": str(row.get("subject", "")),
            "date": str(row.get("date", "")),
            "source": "Fake.csv" if row["label"] == "FAKE" else "True.csv"
        }

    logger.info(f"Created {len(docs)} documents with rich metadata")

    # Split into chunks
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=CHUNK_SIZE,
        chunk_overlap=CHUNK_OVERLAP,
        length_function=len,
    )
    chunks = splitter.split_documents(docs)
    logger.info(f"Split into {len(chunks):,} chunks")

    # Add to FAISS
    logger.info("Adding chunks to FAISS vectorstore...")
    vectorstore_manager.add_documents(chunks)

    logger.success("Historical knowledge base built successfully!")
    logger.success(f"Backend: {vectorstore_manager.active_backend.upper()}")
    logger.success(f"Total chunks: {vectorstore_manager.count():,}")
    logger.success("Next → python scripts/ingest_rss.py")


if __name__ == "__main__":
    main()