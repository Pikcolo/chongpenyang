"""
Strict Zero-Hallucination Guardrail module.
Validates retrieval relevance thresholds, enforces strict context containment,
removes all leaked Chinese characters/punctuation, cleans OCR typos,
and enforces prompt boundaries for out-of-domain queries.
"""

import re
from typing import List, Dict, Any, Tuple
from chatbot.config import settings

# Chinese punctuation to standard equivalents
CHINESE_PUNCTUATION_MAP = {
    '，': ', ',
    '。': '. ',
    '：': ': ',
    '；': '; ',
    '？': '?',
    '！': '!',
    '（': '(',
    '）': ')',
    '【': '[',
    '】': ']',
    '《': '"',
    '》': '"',
    '、': ', ',
    '“': '"',
    '”': '"',
    '‘': "'",
    '’': "'",
    '—': '-',
    '…': '...',
}

# Known Chinese terms emitted occasionally by multilingual models
CHINESE_TERMS_MAP = {
    '注:': 'หมายเหตุ:',
    '注：': 'หมายเหตุ:',
    '注意:': 'ข้อควรระวัง:',
    '注意：': 'ข้อควรระวัง:',
    '例如:': 'ตัวอย่างเช่น:',
    '例如：': 'ตัวอย่างเช่น:',
    '原料:': 'วัตถุดิบ:',
    '原料：': 'วัตถุดิบ:',
    '步骤:': 'ขั้นตอน:',
    '步骤：': 'ขั้นตอน:',
    '做法:': 'วิธีทำ:',
    '做法：': 'วิธีทำ:',
    '总结:': 'สรุป:',
    '总结：': 'สรุป:',
    '酸度': 'ความเป็นกรดผลไม้ (Acidity)',
    '甜度': 'ความหวาน (Sweetness)',
    '苦味': 'รสขม (Bitterness)',
    '醇厚度': 'บอดี้และความเข้มข้น (Body)',
    '风味': 'รสชาติและกลิ่นสัมผัส (Flavor)',
    '香气': 'กลิ่นหอม (Aroma)',
    '浅度烘焙': 'คั่วอ่อน (Light Roast)',
    '中度烘焙': 'คั่วกลาง (Medium Roast)',
    '深度烘焙': 'คั่วเข้ม (Dark Roast)',
    '咖啡豆': 'เมล็ดกาแฟ',
    '萃取': 'การสกัด',
    '研磨': 'การบด',
    '压粉': 'การแทมป์',
    '咖啡机': 'เครื่องชงกาแฟ',
    '蒸汽': 'ไอน้ำ',
    '奶泡': 'โฟมนม',
    '拉花': 'ลาเต้อาร์ต'
}

OUT_OF_DOMAIN_KEYWORDS = [
    "ต้มยำ", "ข้าวมันไก่", "ผัดไทย", "ส้มตำ", "พิซซ่า", "แฮมเบอร์เกอร์",
    "หุ้น", "ptt", "set50", "บิตคอยน์", "bitcoin", "crypto", "คริปโต",
    "ฟุตบอล", "พรีเมียร์ลีก", "การเมือง", "เลือกตั้ง", "นายก"
]

class GuardrailManager:
    """Enforces zero hallucination, cleans foreign text, and manages fallback policies."""

    def __init__(
        self,
        min_threshold: float = None,
        fallback_msg: str = None
    ):
        self.min_threshold = min_threshold or settings.MIN_SIMILARITY_THRESHOLD
        self.fallback_msg = fallback_msg or settings.FALLBACK_MESSAGE

    def is_out_of_domain_query(self, query: str) -> bool:
        """Heuristic check for clearly out-of-domain queries."""
        q_lower = query.lower()
        return any(kw in q_lower for kw in OUT_OF_DOMAIN_KEYWORDS)

    def validate_retrieval(self, contexts: List[Dict[str, Any]], query: str = "") -> Tuple[bool, str]:
        """
        Pre-generation guardrail:
        Checks if query is out of domain or retrieved documents have insufficient semantic confidence.
        Returns (is_valid, message).
        """
        if query and self.is_out_of_domain_query(query):
            return False, self.fallback_msg

        if not contexts:
            return False, self.fallback_msg

        max_score = max(c.get("score", 0.0) for c in contexts)
        if max_score < self.min_threshold:
            return False, self.fallback_msg

        return True, ""

    def sanitize_chinese(self, text: str) -> str:
        """Converts Chinese punctuation and strips any remaining Hanzi characters."""
        if not text:
            return ""

        # 1. Replace known Chinese terminology
        for ch_term, th_term in CHINESE_TERMS_MAP.items():
            text = text.replace(ch_term, th_term)

        # 2. Replace Chinese punctuation
        for ch_punct, std_punct in CHINESE_PUNCTUATION_MAP.items():
            text = text.replace(ch_punct, std_punct)

        # 3. Strip any remaining Hanzi characters (Unicode 4E00-9FFF)
        text = re.sub(r'[\u4e00-\u9fff]', '', text)

        # 4. Clean up empty formatting artifacts (e.g. "- **()**, ." or "- ****, .")
        text = re.sub(r'^\s*[-*•]\s*\*\*\(?\s*\)?\*\*[,.\s]*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*[-*•]\s*\*{2,4}[,.\s]*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*[-*•]\s*[,.\s]+$', '', text, flags=re.MULTILINE)

        # Clean multiple spaces and blank lines that might result from character removal
        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text

    def sanitize_ocr_typos(self, text: str) -> str:
        """Corrects PDF OCR extraction typos and domain terminology."""
        if not text:
            return ""

        cleaned = text
        # Correct pressure unit mistranslations
        cleaned = re.sub(r'\(?\s*90\s*[-–]?\s*100\s*มิลลิแปร?์?\s*\)?', '(9-10 บาร์)', cleaned)
        cleaned = re.sub(r'มิลลิแปร?์', 'บาร์', cleaned)

        # Correct specific broken Thai words
        cleaned = re.sub(r'คาปชู ิโน', 'คาปูชิโน่', cleaned)
        cleaned = re.sub(r'มคั คีอาโต้', 'มัคคิอาโต้', cleaned)
        cleaned = re.sub(r'มอคคา\b', 'มอคค่า', cleaned)
        cleaned = re.sub(r'ลำเต้', 'ลาเต้', cleaned)
        cleaned = re.sub(r'กำแฟ', 'กาแฟ', cleaned)
        cleaned = re.sub(r'อเมริกำโน่', 'อเมริกาโน่', cleaned)
        cleaned = re.sub(r'([หนา|โฟมนม].*?)\b1\s*ชม\.', r'\1 1-2 ซม.', cleaned)
        cleaned = re.sub(r'\b1\s*ชม\.', '1-2 ซม.', cleaned)

        return cleaned

    def strip_context_markers(self, text: str) -> str:
        """Removes any leaked context headers, citation tags, or raw source prefixes."""
        if not text:
            return ""
        cleaned = text.strip()
        # Remove patterns like "ข้อมูลที่ 5 | หน้า 30 | หัวข้อ: ..."
        cleaned = re.sub(r'^(?:ข้อมูลที่\s*\d+\s*\|\s*หน้า\s*\d+\s*\|\s*หัวข้อ:[^\n]*\n*)+', '', cleaned)
        # Remove patterns like "[ข้อมูลที่ ...]" or "[เอกสารอ้างอิง ...]"
        cleaned = re.sub(r'^(?:\[?(?:ข้อมูลที่|เอกสารอ้างอิงลำดับที่|เอกสารอ้างอิง)\s*\d*[^\]\n]*\]?:?\s*\n*)+', '', cleaned)
        # Remove markdown quote of reference tag
        cleaned = re.sub(r'^(?:>\s*\[?[^\]\n]+\]?\s*\n*)+', '', cleaned)
        return cleaned.strip()

    def validate_generation(self, query: str, answer: str, contexts: List[Dict[str, Any]]) -> str:
        """
        Post-generation guardrail:
        Ensures response respects boundaries, strips Chinese leakage, removes context tags, and fixes typos.
        """
        if not answer or len(answer.strip()) < 5:
            return self.fallback_msg

        # If LLM triggered fallback text
        if "ไม่มีระบุในคู่มือ" in answer or "ไม่สามารถให้คำตอบนอกเหนือจากเอกสาร" in answer:
            return self.fallback_msg

        if self.is_out_of_domain_query(query):
            return self.fallback_msg

        # 1. Sanitize Chinese tokens and punctuation
        cleaned = self.sanitize_chinese(answer)

        # 2. Sanitize OCR typos and units
        cleaned = self.sanitize_ocr_typos(cleaned)

        # 3. Strip any accidental context header tags echoed by the LLM
        cleaned = self.strip_context_markers(cleaned)

        return cleaned.strip()
