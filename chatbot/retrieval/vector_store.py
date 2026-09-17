"""
Unified Vector Store Manager supporting both ChromaDB and FAISS backends.
Uses Multilingual HuggingFace Embeddings for high-accuracy Thai & Domain retrieval.
"""

import os
import shutil
from typing import List, Tuple
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings

try:
    from langchain_chroma import Chroma
except ImportError:
    Chroma = None

try:
    from langchain_community.vectorstores import FAISS
except ImportError:
    FAISS = None

from chatbot.config import settings

class VectorStoreManager:
    """Manages creation, loading, and querying of dense vector stores."""

    def __init__(self, store_type: str = None, embed_model_name: str = None):
        self.store_type = (store_type or settings.VECTOR_STORE_TYPE).lower()
        self.embed_model_name = embed_model_name or settings.EMBED_MODEL
        self.embeddings = HuggingFaceEmbeddings(
            model_name=self.embed_model_name,
            model_kwargs={"device": settings.EMBED_DEVICE}
        )
        self.chroma_store = None
        self.faiss_store = None

    def build_from_documents(self, documents: List[Document], persist: bool = True):
        """Indexes documents into the configured vector store."""
        if not documents:
            raise ValueError("No documents provided for indexing.")

        print(f"📦 Indexing {len(documents)} documents into {self.store_type.upper()}...")

        if self.store_type == "chroma":
            if Chroma is None:
                raise ImportError("langchain-chroma is required for ChromaDB backend.")
            os.makedirs(settings.CHROMA_PATH, exist_ok=True)
            self.chroma_store = Chroma.from_documents(
                documents=documents,
                embedding=self.embeddings,
                persist_directory=settings.CHROMA_PATH,
                collection_name=settings.COLLECTION_NAME
            )
            print(f"✅ ChromaDB collection '{settings.COLLECTION_NAME}' saved at: {settings.CHROMA_PATH}")
            return self.chroma_store

        elif self.store_type == "faiss":
            if FAISS is None:
                raise ImportError("langchain_community.vectorstores.FAISS is required for FAISS backend.")
            os.makedirs(settings.FAISS_PATH, exist_ok=True)
            self.faiss_store = FAISS.from_documents(
                documents=documents,
                embedding=self.embeddings
            )
            self.faiss_store.save_local(settings.FAISS_PATH)
            print(f"✅ FAISS index saved at: {settings.FAISS_PATH}")
            return self.faiss_store
        else:
            raise ValueError(f"Unsupported vector store type: {self.store_type}")

    def load_existing(self):
        """Loads existing persisted vector store."""
        if self.store_type == "chroma":
            if not os.path.exists(settings.CHROMA_PATH):
                return False
            self.chroma_store = Chroma(
                persist_directory=settings.CHROMA_PATH,
                embedding_function=self.embeddings,
                collection_name=settings.COLLECTION_NAME
            )
            return True
        elif self.store_type == "faiss":
            if not os.path.exists(settings.FAISS_PATH):
                return False
            self.faiss_store = FAISS.load_local(
                settings.FAISS_PATH,
                self.embeddings,
                allow_dangerous_deserialization=True
            )
            return True
        return False

    def similarity_search_with_score(self, query: str, k: int = 5) -> List[Tuple[Document, float]]:
        """Searches nearest neighbor chunks with normalized similarity scores."""
        if self.store_type == "chroma":
            if not self.chroma_store and not self.load_existing():
                return []
            raw_results = self.chroma_store.similarity_search_with_score(query, k=k)
            converted = []
            for doc, dist in raw_results:
                sim = 1.0 / (1.0 + max(0.0, float(dist)))
                converted.append((doc, sim))
            return converted
        elif self.store_type == "faiss":
            if not self.faiss_store and not self.load_existing():
                return []
            # FAISS returns L2 distance or cosine distance
            raw_results = self.faiss_store.similarity_search_with_score(query, k=k)
            converted = []
            for doc, dist in raw_results:
                # Convert distance to approximate [0, 1] similarity score
                sim = 1.0 / (1.0 + float(dist))
                converted.append((doc, sim))
            return converted
        return []
