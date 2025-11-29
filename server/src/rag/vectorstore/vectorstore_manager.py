# src/rag/vectorstore/vectorstore_manager.py
"""
Unified VectorStore Manager for TruthPulse Explainer
Smart auto-detection: Chroma (dev) → FAISS (production)
Now creates empty FAISS if nothing exists → no more crashes!
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import List, Optional, Dict, Any, Tuple, Literal, Union

from loguru import logger
from langchain_community.vectorstores import Chroma, FAISS
from langchain_core.documents import Document

from src.rag.vectorstore.embedding_utils import get_langchain_embeddings

# Config
from config import VECTORSTORE_PATH


class VectorStoreManager:
    def __init__(self, prefer_chroma: bool = True):
        self.prefer_chroma = prefer_chroma
        self.embeddings = get_langchain_embeddings()
        self.vectorstore: Optional[Union[Chroma, FAISS]] = None
        self.active_backend: Literal["chroma", "faiss", "none"] = "none"
        self._initialize()

    def _initialize(self) -> None:
        chroma_path = Path(VECTORSTORE_PATH)

        # 1. Try Chroma first (only if user wants it and it exists)
        if self.prefer_chroma and chroma_path.exists():
            try:
                logger.info(f"Loading Chroma from {VECTORSTORE_PATH}")
                self.vectorstore = Chroma(
                    persist_directory=VECTORSTORE_PATH,
                    embedding_function=self.embeddings
                )
                count = self.vectorstore._collection.count()
                logger.success(f"Chroma loaded → {count:,} chunks")
                self.active_backend = "chroma"
                return
            except Exception as e:
                logger.warning(f"Chroma load failed: {e}")

        # 2. Try loading existing FAISS
        faiss_dir = Path("vectorstore/faiss")
        if faiss_dir.exists() and any(faiss_dir.glob("*.faiss")):
            try:
                logger.info("Loading existing FAISS index...")
                self.vectorstore = FAISS.load_local(
                    folder_path=str(faiss_dir),
                    embeddings=self.embeddings,
                    index_name="index",
                    allow_dangerous_deserialization=True,
                )
                count = len(self.vectorstore.docstore._dict)
                logger.success(f"FAISS loaded → {count:,} chunks (production mode)")
                self.active_backend = "faiss"
                return
            except Exception as e:
                logger.warning(f"FAISS load failed: {e}")

        # 3. NOTHING EXISTS → CREATE EMPTY FAISS (this is the key fix!)
        logger.info("No vectorstore found → creating new empty FAISS index")
        dummy_doc = Document(page_content="placeholder", metadata={"source": "init"})
        self.vectorstore = FAISS.from_documents([dummy_doc], self.embeddings)
        # Remove dummy
        dummy_id = list(self.vectorstore.docstore._dict.keys())[0]
        self.vectorstore.delete([dummy_id])
        self.active_backend = "faiss"
        logger.success("Empty FAISS vectorstore created — ready for first ingestion")

    # === All your methods below stay the same ===
    def similarity_search(self, query: str, k: int = 6, filter=None) -> List[Document]:
        if not self.vectorstore:
            return []
        return self.vectorstore.similarity_search(query, k=k, filter=filter)

    def similarity_search_with_score(self, query: str, k: int = 6, filter=None):
        if not self.vectorstore:
            return []
        return self.vectorstore.similarity_search_with_score(query, k=k, filter=filter)

    def add_documents(self, documents: List[Document]) -> List[str]:
        if not self.vectorstore:
            logger.error("No vectorstore to add to!")
            return []
        ids = self.vectorstore.add_documents(documents)
        logger.info(f"Added {len(documents)} documents → total: {self.count():,}")
        return ids

    def save_to_faiss(self, path: str = "vectorstore/faiss") -> None:
        if not self.vectorstore:
            logger.error("No data to export")
            return
        logger.info("Exporting current vectorstore → FAISS")
        os.makedirs(path, exist_ok=True)
        self.vectorstore.save_local(folder_path=path, index_name="index")
        logger.success(f"FAISS exported → {path}")

    def count(self) -> int:
        if not self.vectorstore:
            return 0
        if isinstance(self.vectorstore, Chroma):
            return self.vectorstore._collection.count()
        return len(self.vectorstore.docstore._dict)

    def status(self) -> Dict[str, Any]:
        return {
            "active_backend": self.active_backend,
            "document_count": self.count(),
            "embedding_model": self.embeddings.model_name,
        }


# Singleton instance
vectorstore_manager = VectorStoreManager(prefer_chroma=False)


if __name__ == "__main__":
    print("VectorStore Status:")
    print(f"   Backend: {vectorstore_manager.active_backend.upper()}")
    print(f"   Documents: {vectorstore_manager.count():,}")