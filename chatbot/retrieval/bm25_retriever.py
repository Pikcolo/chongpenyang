"""
Sparse lexical retriever using BM25Okapi with PyThaiNLP morphological segmentation.
"""

from typing import List, Tuple
import pythainlp
from rank_bm25 import BM25Okapi
from langchain_core.documents import Document

import sys
if hasattr(sys.stdout, 'reconfigure'):
    try:
        sys.stdout.reconfigure(encoding='utf-8')
    except Exception:
        pass

class BM25Retriever:
    """Performs sparse keyword retrieval using BM25 over Thai segmented corpus."""

    def __init__(self, documents: List[Document] = None):
        self.documents: List[Document] = []
        self.bm25: BM25Okapi = None
        if documents:
            self.fit(documents)

    def fit(self, documents: List[Document]):
        """Indexes documents by tokenizing Thai content."""
        self.documents = list(documents)
        tokenized_corpus = [
            pythainlp.word_tokenize(doc.page_content, engine='newmm')
            for doc in self.documents
        ]
        self.bm25 = BM25Okapi(tokenized_corpus)
        try:
            print(f"✅ BM25 indexed {len(self.documents)} documents.")
        except Exception:
            print(f"[OK] BM25 indexed {len(self.documents)} documents.")

    def search(self, query: str, top_k: int = 5) -> List[Tuple[Document, float]]:
        """Searches BM25 index and returns list of (Document, score)."""
        if not self.bm25 or not self.documents:
            return []

        tokens = pythainlp.word_tokenize(query, engine='newmm')
        scores = self.bm25.get_scores(tokens)

        # Get top-k indices with score > 0
        ranked_indices = sorted(
            range(len(scores)),
            key=lambda i: scores[i],
            reverse=True
        )[:top_k]

        results = []
        for idx in ranked_indices:
            if scores[idx] > 0.0:
                results.append((self.documents[idx], float(scores[idx])))

        return results
