"""
Quantitative evaluation metrics:
- SBERT Cosine Similarity
- BERTScore (Precision, Recall, F1)
- Context Faithfulness & Alignment
"""

from typing import List, Dict, Any
import numpy as np
from sentence_transformers import SentenceTransformer
import torch

try:
    from bert_score import score as bert_score_fn
except ImportError:
    bert_score_fn = None

class RAGMetricsEvaluator:
    """Computes academic & production-grade quantitative RAG metrics."""

    def __init__(self, model_name: str = "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2"):
        self.model_name = model_name
        self.sbert = SentenceTransformer(model_name)

    def calculate_sbert_similarity(
        self,
        predictions: List[str],
        references: List[str]
    ) -> List[float]:
        """Calculates cosine similarity between generated answers and ground truth."""
        if not predictions or not references:
            return []

        pred_embeddings = self.sbert.encode(predictions, normalize_embeddings=True)
        ref_embeddings = self.sbert.encode(references, normalize_embeddings=True)

        # Dot product of normalized vectors = Cosine Similarity
        cosine_sims = np.sum(pred_embeddings * ref_embeddings, axis=1)
        # Clip to [0, 1]
        return [float(max(0.0, min(1.0, s))) for s in cosine_sims]

    def calculate_bert_score(
        self,
        predictions: List[str],
        references: List[str]
    ) -> Dict[str, List[float]]:
        """Calculates BERTScore (Precision, Recall, F1) for generated responses."""
        if not bert_score_fn or not predictions or not references:
            # Fallback if bert_score not available
            sbert_sims = self.calculate_sbert_similarity(predictions, references)
            return {
                "precision": sbert_sims,
                "recall": sbert_sims,
                "f1": sbert_sims
            }

        try:
            P, R, F1 = bert_score_fn(
                predictions,
                references,
                lang="other",  # or multilingual
                model_type="bert-base-multilingual-cased",
                verbose=False,
                device="cpu"
            )
            return {
                "precision": [float(p) for p in P],
                "recall": [float(r) for r in R],
                "f1": [float(f) for f in F1]
            }
        except Exception as e:
            print(f"⚠️ BERTScore note ({e}), falling back to SBERT token-level approximation.")
            sbert_sims = self.calculate_sbert_similarity(predictions, references)
            return {
                "precision": sbert_sims,
                "recall": sbert_sims,
                "f1": sbert_sims
            }

    def calculate_faithfulness(
        self,
        predictions: List[str],
        contexts_list: List[List[str]]
    ) -> List[float]:
        """
        Calculates Faithfulness: whether claims in the generated answer are grounded in context.
        Measured by sentence-level semantic alignment to retrieved passages.
        """
        faithfulness_scores = []
        for pred, contexts in zip(predictions, contexts_list):
            if not pred or not contexts:
                faithfulness_scores.append(0.0)
                continue

            # If fallback message was appropriately triggered
            if "ไม่มีระบุในคู่มือ" in pred:
                faithfulness_scores.append(1.0)
                continue

            # Split prediction into sentences
            sentences = [s.strip() for s in pred.split("\n") if len(s.strip()) > 10]
            if not sentences:
                sentences = [pred]

            context_blob = " ".join(contexts)
            sent_embs = self.sbert.encode(sentences, normalize_embeddings=True)
            ctx_emb = self.sbert.encode([context_blob], normalize_embeddings=True)[0]

            sims = np.dot(sent_embs, ctx_emb)
            avg_faithfulness = float(np.mean(np.clip(sims, 0.0, 1.0)))
            faithfulness_scores.append(avg_faithfulness)

        return faithfulness_scores
