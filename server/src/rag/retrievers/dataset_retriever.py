# src/rag/retrievers/dataset_retriever.py
import os
from pathlib import Path
from typing import List, Optional, Union, Dict, Any
from loguru import logger

from langchain_community.vectorstores import Chroma, FAISS
from langchain_core.documents import Document
from langchain_community.embeddings import HuggingFaceEmbeddings

from config import VECTORSTORE_PATH, FAISS_INDEX_PATH, FAISS_PK_PATH, EMBEDDING_MODEL_NAME


class DatasetRetriever:
    """
    Hybrid retriever for the fake/real news dataset stored in Chroma (primary) or FAISS (fallback).
    Supports semantic search + metadata filtering (e.g., only REAL articles, politics, etc.).
    """

    def __init__(
        self,
        embedding_model_name: str = EMBEDDING_MODEL_NAME,
        use_faiss: bool = False,
        k: int = 6,
    ):
        self.k = k
        self.embeddings = HuggingFaceEmbeddings(
            model_name=embedding_model_name,
            model_kwargs={"device": "cpu"},
            encode_kwargs={"normalize_embeddings": True},
        )

        self.vectorstore = None
        self.use_faiss = use_faiss

        self._load_vectorstore()

    def _load_vectorstore(self):
        """Load Chroma (preferred) or fall back to FAISS if available."""
        chroma_path = Path(VECTORSTORE_PATH)

        if chroma_path.exists() and not self.use_faiss:
            logger.info(f"Loading Chroma vectorstore from {VECTORSTORE_PATH}")
            try:
                self.vectorstore = Chroma(
                    persist_directory=VECTORSTORE_PATH,
                    embedding_function=self.embeddings
                )
                logger.success("Chroma vectorstore loaded successfully")
                return
            except Exception as e:
                logger.warning(f"Failed to load Chroma: {e}")

        # Fallback to FAISS
        if Path(FAISS_INDEX_PATH).exists() and Path(FAISS_PK_PATH).exists():
            logger.info("Falling back to FAISS vectorstore")
            self.vectorstore = FAISS.load_local(
                folder_path="vectorstore/faiss",
                embeddings=self.embeddings,
                index_name="index",
                allow_dangerous_deserialization=True
            )
            logger.success("FAISS vectorstore loaded")
        else:
            raise RuntimeError(
                "No valid vectorstore found!\n"
                "Run: python scripts/prepare_vectorstore.py first."
            )

    def retrieve(
        self,
        query: str,
        k: Optional[int] = None,
        filter_label: Optional[str] = None,        # "REAL", "FAKE", or None
        filter_subject: Optional[str] = None,      # e.g., "politics", "world"
        min_date: Optional[str] = None,            # YYYY-MM-DD
        reliable_only: bool = False,
    ) -> List[Document]:
        """
        Retrieve relevant documents with optional metadata filtering.
        """
        k = k or self.k

        # Build metadata filter
        where_clause: Dict[str, Any] = {}
        if filter_label:
            where_clause["label"] = filter_label.upper()
        if filter_subject:
            where_clause["subject"] = {"$eq": filter_subject.lower()}

        # Chroma supports date filtering via string comparison
        if min_date:
            where_clause["date"] = {"$gte": min_date}

        # Custom reliability (if you added it later)
        if reliable_only:
            where_clause["reliable"] = True

        try:
            if isinstance(self.vectorstore, Chroma):
                docs = self.vectorstore.similarity_search(
                    query,
                    k=k,
                    filter=where_clause if where_clause else None
                )
            else:  # FAISS
                # FAISS doesn't support native filtering → post-filter
                docs = self.vectorstore.similarity_search(query, k=k * 3)
                docs = self._post_filter_docs(docs, where_clause)

            logger.debug(f"Retrieved {len(docs)} documents for query: {query[:60]}...")
            return docs

        except Exception as e:
            logger.error(f"Retrieval failed: {e}")
            return []

    def _post_filter_docs(self, docs: List[Document], where_clause: Dict) -> List[Document]:
        """Manual filtering for FAISS (since it doesn't support metadata filters natively)."""
        filtered = []
        for doc in docs:
            meta = doc.metadata
            match = True
            for key, val in where_clause.items():
                if meta.get(key) != val:
                    match = False
                    break
            if match:
                filtered.append(doc)
        return filtered[:self.k]

    def retrieve_real_news(self, query: str, k: int = 5) -> List[Document]:
        """Convenience: Get only verified real news articles."""
        return self.retrieve(query, k=k, filter_label="REAL")

    def retrieve_fake_examples(self, query: str, k: int = 5) -> List[Document]:
        """Convenience: Get known fake articles matching the claim pattern."""
        return self.retrieve(query, k=k, filter_label="FAKE")

    def as_retriever(self, **kwargs):
        """Return as LangChain retriever (for use in chains)."""
        from langchain_core.retrievers import Retriever

        class DatasetRetrieverWrapper(Retriever):
            parent = self

            def get_relevant_documents(self, query: str) -> List[Document]:
                return self.parent.retrieve(query, **kwargs)

            async def aget_relevant_documents(self, query: str):
                return self.get_relevant_documents(query)

        return DatasetRetrieverWrapper()


dataset_retriever = DatasetRetriever()


# Example usage when running directly
if __name__ == "__main__":
    retriever = DatasetRetriever()
    docs = retriever.retrieve("Hillary Clinton sold weapons to ISIS", filter_label="FAKE")
    for d in docs[:3]:
        print(f"[{d.metadata.get('label')}] {d.metadata.get('title', '')[:80]}")
        print(f"→ {d.page_content[:200]}...\n")