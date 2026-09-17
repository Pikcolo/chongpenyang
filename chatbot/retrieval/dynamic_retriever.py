"""
Dynamic Top-k query analyzer, Token Budget Manager, and Hybrid Pipeline Orchestrator.
"""

from typing import List, Dict, Any, Tuple
import re
from langchain_core.documents import Document

from chatbot.config import settings
from chatbot.retrieval.vector_store import VectorStoreManager
from chatbot.retrieval.bm25_retriever import BM25Retriever
from chatbot.retrieval.fusion import reciprocal_rank_fusion, relative_score_fusion
from chatbot.retrieval.reranker import CrossEncoderReranker

COMPLEX_INTENT_KEYWORDS = [
    "เปรียบเทียบ", "แตกต่าง", "ต่างกัน", "ข้อดีข้อเสีย",
    "สาเหตุ", "ทำไม", "แก้ปัญหา", "อย่างไร", "วิธี", "ขั้นตอน",
    "สูตร", "ทั้งหมด", "รายละเอียด", "ตาราง", "เทียบ"
]

class DynamicHybridRetriever:
    """
    Production-Grade Hybrid Retriever combining:
    1. Dynamic Top-k based on query complexity
    2. Dense Vector Search (ChromaDB / FAISS)
    3. Sparse Keyword Search (BM25 with Thai tokenization)
    4. Fusion Engine (Reciprocal Rank Fusion / Relative Score)
    5. Cross-Encoder Re-ranking
    6. Token Budget Management & Parent Document Context expansion
    """

    def __init__(
        self,
        vector_store: VectorStoreManager,
        bm25_retriever: BM25Retriever,
        reranker: CrossEncoderReranker = None
    ):
        self.vector_store = vector_store
        self.bm25 = bm25_retriever
        self.reranker = reranker

    def calculate_dynamic_top_k(self, query: str) -> int:
        """
        Dynamically determines optimal candidate top-k:
        - Short factoid query -> 3
        - Normal inquiry -> 5
        - Complex / Comparative / Procedural -> 7 to 8
        """
        query_len = len(query.strip())
        is_complex = any(kw in query for kw in COMPLEX_INTENT_KEYWORDS)

        if is_complex or query_len > 60:
            k = min(settings.MAX_TOP_K, 8)
        elif query_len < 20 and not is_complex:
            k = max(settings.MIN_TOP_K, 3)
        else:
            k = settings.TOP_K_DEFAULT
        return k

    def manage_token_budget(
        self,
        ranked_docs: List[Tuple[Document, float]],
        max_tokens: int = None
    ) -> List[Dict[str, Any]]:
        """
        Packs documents into the LLM context within the token budget.
        Expands to Parent context if available and within budget, otherwise uses Child context.
        """
        budget = max_tokens or settings.MAX_CONTEXT_TOKENS
        # Rough estimation: 1 Thai token ~= 2.5 - 3 characters
        current_char_count = 0
        max_char_budget = budget * 3

        selected_items = []
        seen_parents = set()

        for doc, score in ranked_docs:
            parent_id = doc.metadata.get("parent_id")
            parent_content = doc.metadata.get("parent_content")
            
            # Prefer parent context if not already added and fits budget
            content_to_use = doc.page_content
            use_parent = False
            if parent_content and parent_id and parent_id not in seen_parents:
                if (current_char_count + len(parent_content)) <= max_char_budget:
                    content_to_use = parent_content
                    use_parent = True
                    seen_parents.add(parent_id)

            char_len = len(content_to_use)
            if current_char_count + char_len > max_char_budget and selected_items:
                # If cannot fit, break or keep child if child fits
                if (current_char_count + len(doc.page_content)) <= max_char_budget:
                    content_to_use = doc.page_content
                    char_len = len(content_to_use)
                else:
                    continue

            current_char_count += char_len
            selected_items.append({
                "content": content_to_use,
                "score": float(score),
                "page": doc.metadata.get("page", 1),
                "topic_title": doc.metadata.get("topic_title", "คู่มือบาริสต้ามืออาชีพ"),
                "document_name": doc.metadata.get("document_name", "คู่มือประกอบการฝึกอบรม หลักสูตร: บาริสต้ามืออาชีพ"),
                "is_table": doc.metadata.get("is_table", False),
                "is_parent": use_parent,
                "child_id": doc.metadata.get("child_id", "")
            })

        return selected_items

    def retrieve(self, query: str) -> Dict[str, Any]:
        """Executes full dynamic hybrid retrieval pipeline."""
        dynamic_k = self.calculate_dynamic_top_k(query)
        candidate_multiplier = 3  # Retrieve more candidates for reranking
        initial_k = dynamic_k * candidate_multiplier

        # 1. Dense Search
        dense_results = self.vector_store.similarity_search_with_score(query, k=initial_k)

        # 2. Sparse BM25 Search
        sparse_results = self.bm25.search(query, top_k=initial_k)

        # 3. Fusion
        if settings.FUSION_ALGORITHM == "relative_score":
            fused = relative_score_fusion(
                dense_results,
                sparse_results,
                dense_weight=settings.DENSE_WEIGHT,
                sparse_weight=settings.SPARSE_WEIGHT
            )
        else:
            fused = reciprocal_rank_fusion(dense_results, sparse_results, k=settings.RRF_K)

        # 4. Cross-Encoder Re-ranking
        if self.reranker and settings.RERANKER_ENABLED:
            reranked = self.reranker.rerank(query, fused, top_n=dynamic_k)
        else:
            reranked = fused[:dynamic_k]

        # 5. Token Budget Management & Context Assembly
        budgeted_contexts = self.manage_token_budget(reranked)

        return {
            "query": query,
            "dynamic_k": dynamic_k,
            "contexts": budgeted_contexts,
            "raw_candidates_count": len(fused)
        }
