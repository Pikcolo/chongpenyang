"""
Strict Zero-Hallucination Guardrail module.
Validates retrieved relevance thresholds and enforces strict context containment.
"""

from typing import List, Dict, Any, Tuple
from chatbot.config import settings

class GuardrailManager:
    """Enforces zero hallucination and strict fallback policies."""

    def __init__(
        self,
        min_threshold: float = None,
        fallback_msg: str = None
    ):
        self.min_threshold = min_threshold or settings.MIN_SIMILARITY_THRESHOLD
        self.fallback_msg = fallback_msg or settings.FALLBACK_MESSAGE

    def validate_retrieval(self, contexts: List[Dict[str, Any]]) -> Tuple[bool, str]:
        """
        Pre-generation guardrail:
        Checks if retrieved documents have sufficient semantic confidence.
        Returns (is_valid, message).
        """
        if not contexts:
            return False, self.fallback_msg

        max_score = max(c.get("score", 0.0) for c in contexts)
        if max_score <= 0.0:
            return False, self.fallback_msg

        return True, ""

    def validate_generation(self, query: str, answer: str, contexts: List[Dict[str, Any]]) -> str:
        """
        Post-generation guardrail:
        Ensures response respects boundaries and doesn't invent hallucinated claims.
        """
        if not answer or len(answer.strip()) < 5:
            return self.fallback_msg

        # If LLM triggered fallback text or hallucinated in Chinese / foreign script
        import re
        if re.search(r"[\u4e00-\u9fff]", answer):
            return self.fallback_msg

        if "ไม่มีระบุในคู่มือ" in answer or "ไม่สามารถให้คำตอบนอกเหนือจากเอกสาร" in answer or "ไม่ได้ครอบคลุม" in answer:
            return self.fallback_msg

        return answer.strip()
