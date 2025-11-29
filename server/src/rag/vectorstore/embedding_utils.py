# src/rag/vectorstore/embedding_utils.py
"""
embedding_utils.py – Centralized, optimized embedding management
100% Windows compatible – no "auto" crash, no syntax errors
"""

from __future__ import annotations

import os
from typing import List, Union, Optional
from functools import lru_cache

import torch
from loguru import logger
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import HuggingFaceEmbeddings

from config import EMBEDDING_MODEL_NAME


@lru_cache(maxsize=1)
def get_embedding_model(
    model_name: str = EMBEDDING_MODEL_NAME,
    device: Optional[str] = None,
    normalize_embeddings: bool = True,
    cache_folder: Optional[str] = None,
) -> SentenceTransformer:
    """Load and cache the SentenceTransformer model with safe device detection."""
    if device is None:
        if torch.cuda.is_available():
            device = "cuda"
            logger.info(f"GPU detected → using {torch.cuda.get_device_name(0)}")
        elif torch.backends.mps.is_available():
            device = "mps"
            logger.info("Apple Silicon MPS detected → using GPU acceleration")
        else:
            device = "cpu"
            logger.info("Using CPU for embeddings")

    logger.info(f"Loading embedding model: {model_name} → {device}")

    model = SentenceTransformer(
        model_name,
        device=device,
        cache_folder=cache_folder or os.getenv("SENTENCE_TRANSFORMERS_HOME"),
    )

    if normalize_embeddings:
        logger.info("Embeddings will be L2-normalized")

    return model


def get_langchain_embeddings() -> HuggingFaceEmbeddings:
    """LangChain-compatible embeddings – safe device handling (no 'auto')"""
    import torch

    if torch.cuda.is_available():
        device = "cuda"
    elif torch.backends.mps.is_available():
        device = "mps"
    else:
        device = "cpu"

    logger.info(f"Creating LangChain embeddings on device: {device.upper()}")

    return HuggingFaceEmbeddings(
        model_name=EMBEDDING_MODEL_NAME,
        model_kwargs={"device": device},
        encode_kwargs={"normalize_embeddings": True},
        cache_folder=os.getenv("SENTENCE_TRANSFORMERS_HOME"),
    )


def embed_texts(
    texts: Union[str, List[str]],
    batch_size: int = 32,
    show_progress: bool = False,
) -> List[List[float]]:
    model = get_embedding_model()
    texts = [texts] if isinstance(texts, str) else texts
    embeddings = model.encode(
        texts,
        batch_size=batch_size,
        show_progress_bar=show_progress,
        normalize_embeddings=True,
        convert_to_numpy=True,
    )
    return embeddings.tolist()


def embed_query(text: str) -> List[float]:
    return embed_texts(text, batch_size=1)[0]


if __name__ == "__main__":
    logger.info("Testing embedding utils...")
    vec = embed_query("Cyclone Remal has hit West Bengal")
    logger.success(f"Embedding works! Dimension: {len(vec)}")
    print("embedding_utils.py is ready")