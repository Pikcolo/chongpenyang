"""
Cross-Encoder Re-ranker module for rescoring retrieved candidate documents.
"""

from typing import List, Tuple
from langchain_core.documents import Document
from sentence_transformers import CrossEncoder

from chatbot.config import settings

class CrossEncoderReranker:
    """Re-ranks candidate passages using a deep Cross-Encoder model."""

    def __init__(self, model_name: str = None):
        self.model_name = model_name or settings.RERANKER_MODEL
        self.model = None
        self._load_model()

    def _load_model(self):
        try:
            print(f"🔄 Loading Cross-Encoder Re-ranker: '{self.model_name}'...")
            self.model = CrossEncoder(self.model_name, device=settings.EMBED_DEVICE)
            print("✅ Cross-Encoder Re-ranker ready.")
        except Exception as e:
            print(f"⚠️ Warning: Could not load CrossEncoder ('{self.model_name}'): {e}")
            print("ℹ️ Falling back to Fusion ranking order.")
            self.model = None

    def rerank(
        self,
        query: str,
        candidates: List[Tuple[Document, float]],
        top_n: int = 4
    ) -> List[Tuple[Document, float]]:
        """Re-ranks a list of candidate documents against the query."""
        if not candidates:
            return []

        if not self.model:
            # Fallback to current score order
            return candidates[:top_n]

        docs = [doc for doc, _ in candidates]
        pairs = [(query, doc.page_content) for doc in docs]

        try:
            raw_scores = self.model.predict(pairs)
            import numpy as np
            # Convert raw logits to [0, 1] probability via sigmoid
            sigmoid_scores = 1.0 / (1.0 + np.exp(-np.array(raw_scores, dtype=float)))
            scored_docs = list(zip(docs, [float(s) for s in sigmoid_scores]))
            scored_docs.sort(key=lambda x: x[1], reverse=True)
            return scored_docs[:top_n]
        except Exception as e:
            print(f"⚠️ Error during re-ranking: {e}")
            return candidates[:top_n]
