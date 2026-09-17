"""
Fusion Algorithms for combining Dense and Sparse retrieval results.
Implements Reciprocal Rank Fusion (RRF) and Relative Score Fusion (Convex Combination).
"""

from typing import List, Tuple, Dict
from langchain_core.documents import Document

def get_doc_identifier(doc: Document) -> str:
    """Returns unique key for deduplication and rank fusion."""
    return doc.metadata.get("child_id") or doc.page_content[:100]

def reciprocal_rank_fusion(
    dense_results: List[Tuple[Document, float]],
    sparse_results: List[Tuple[Document, float]],
    k: int = 60
) -> List[Tuple[Document, float]]:
    """
    Combines ranked lists using Reciprocal Rank Fusion (RRF).
    Formula: RRF_score(d) = sum(1 / (k + rank_i(d)))
    """
    scores: Dict[str, float] = {}
    doc_map: Dict[str, Document] = {}

    # Accumulate Dense ranks
    for rank, (doc, _) in enumerate(dense_results, start=1):
        doc_id = get_doc_identifier(doc)
        doc_map[doc_id] = doc
        scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank))

    # Accumulate Sparse ranks
    for rank, (doc, _) in enumerate(sparse_results, start=1):
        doc_id = get_doc_identifier(doc)
        doc_map[doc_id] = doc
        scores[doc_id] = scores.get(doc_id, 0.0) + (1.0 / (k + rank))

    # Sort documents by accumulated RRF score descending
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    return [(doc_map[doc_id], score) for doc_id, score in sorted_items]

def relative_score_fusion(
    dense_results: List[Tuple[Document, float]],
    sparse_results: List[Tuple[Document, float]],
    dense_weight: float = 0.5,
    sparse_weight: float = 0.5
) -> List[Tuple[Document, float]]:
    """
    Combines results via Min-Max Normalized Relative Score Fusion (Convex Combination).
    Score(d) = (w_dense * norm_dense) + (w_sparse * norm_sparse)
    """
    def min_max_normalize(results: List[Tuple[Document, float]]) -> Dict[str, float]:
        if not results:
            return {}
        raw_scores = [s for _, s in results]
        min_s = min(raw_scores)
        max_s = max(raw_scores)
        span = max_s - min_s
        normalized = {}
        for doc, s in results:
            doc_id = get_doc_identifier(doc)
            normalized[doc_id] = 1.0 if span == 0 else (s - min_s) / span
        return normalized

    norm_dense = min_max_normalize(dense_results)
    norm_sparse = min_max_normalize(sparse_results)

    doc_map: Dict[str, Document] = {}
    for doc, _ in dense_results:
        doc_map[get_doc_identifier(doc)] = doc
    for doc, _ in sparse_results:
        doc_map[get_doc_identifier(doc)] = doc

    combined_scores: Dict[str, float] = {}
    all_doc_ids = set(norm_dense.keys()).union(set(norm_sparse.keys()))

    for doc_id in all_doc_ids:
        d_score = norm_dense.get(doc_id, 0.0)
        s_score = norm_sparse.get(doc_id, 0.0)
        final_score = (dense_weight * d_score) + (sparse_weight * s_score)
        combined_scores[doc_id] = final_score

    sorted_items = sorted(combined_scores.items(), key=lambda x: x[1], reverse=True)
    return [(doc_map[doc_id], score) for doc_id, score in sorted_items]
