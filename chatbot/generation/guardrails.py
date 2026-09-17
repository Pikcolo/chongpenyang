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
    # Programming & Code
    "python", "javascript", "java", "c++", "c#", "html", "css", "sql", "php", "ruby", "swift", "golang", "rust",
    "โค้ด", "code", "เขียนโค้ด", "เขียนโปรแกรม", "script", "สคริปต์", "โปรแกรมเมอร์", "developer", "coding",
    
    # Illicit / Drugs / Non-coffee substances
    "ท่อม", "กระท่อม", "น้ำท่อม", "ต้มท่อม", "กัญชา", "กัญชง", "ยาบ้า", "ยาอี", "ยาไอซ์", "ยาเสพติด",
    "บุหรี่", "เหล้า", "เบียร์", "สุรา", "ไวน์", "แอลกอฮอล์",
    
    # Non-coffee Cooking & Food
    "ต้มยำ", "ข้าวมันไก่", "ผัดไทย", "ส้มตำ", "พิซซ่า", "แฮมเบอร์เกอร์", "ก๋วยเตี๋ยว", "แกงส้ม",
    "หมูกระทะ", "ชาบู", "ไข่เจียว", "ข้าวผัด", "แกงเขียวหวาน", "อาหารตามสั่ง", "ทำเค้ก",
    
    # Financial / Stocks / Crypto / Gambling / Politics
    "หุ้น", "ptt", "set50", "บิตคอยน์", "bitcoin", "crypto", "คริปโต", "พรีเมียร์ลีก",
    "การเมือง", "เลือกตั้ง", "นายก", "หวย", "ลอตเตอรี่", "คาสิโน", "บาคาร่า",
    
    # General non-coffee tasks
    "การบ้าน", "แต่งกลอน", "เรียงความ", "แปลภาษา", "แคลคูลัส", "สมการ"
]

PROMPT_INJECTION_KEYWORDS = [
    # System / Debug / Admin Override
    "debug_mode", "debug mode", "admin override", "admin_override", "admin", "ผู้ดูแลระบบ",
    "โหมดบำรุงรักษา", "โหมดทดสอบ", "maintenance mode", "developer mode", "dan mode",
    
    # Prompt Leaking & Instructions
    "system instruction", "system instructions", "system prompt", "system message",
    "คำสั่งระบบ", "คำสั่งดั้งเดิม", "คำสั่งเริ่มต้น", "คำสั่งแรก",
    "โปรดแสดง system", "แสดง prompt", "คาย prompt", "เผยคำสั่ง", "เปิดเผย prompt",
    "ignore previous instructions", "ignore all previous instructions", "ลืมคำสั่ง", "ยกเลิกคำสั่งก่อนหน้า",
    "jailbreak", "bypass",
    
    # RAG Architecture / Metadata Extraction
    "chunking id", "chunk id", "chunk_id", "chunking",
    "ไปป์ไลน์ rag", "rag pipeline", "document sources",
    "รายชื่อเอกสารและ chunking", "chunking id ทั้งหมด",
    
    # Secrets & Config
    "secret_key", "api_key", "channel_secret", "access_token", "line_bot_api"
]

# Valid coffee drinks recognized in the 53-page manual
VALID_MANUAL_DRINKS = [
    "เอสเพรสโซ่", "espresso", "อเมริกาโน่", "americano", "ลาเต้", "latte",
    "คาปูชิโน่", "cappuccino", "มอคค่า", "mocha", "กาแฟส้ม", "orange",
    "กาแฟพีช", "peach", "กาแฟน้ำผึ้งมะนาว", "honey lemon", "ลาเต้มิ้นท์", "mint",
    "dirty", "เดอร์ตี้", "flat white", "มัคคิอาโต้", "macchiato", "ristretto",
    "lungo", "doppio", "cold brew", "cold drip", "french press", "syphon",
    "aeropress", "moka pot", "drip", "ดริป", "pourover", "ช็อต", "shot"
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

    def is_prompt_injection(self, query: str) -> bool:
        """Detects prompt injection, jailbreak attempts, and system instruction leaking attacks."""
        if not query:
            return False
        q_lower = query.lower()
        return any(kw in q_lower for kw in PROMPT_INJECTION_KEYWORDS)

    def is_out_of_domain_query(self, query: str) -> bool:
        """Heuristic check for clearly out-of-domain queries."""
        q_lower = query.lower()
        return any(kw in q_lower for kw in OUT_OF_DOMAIN_KEYWORDS)

    def is_fabricated_drink_query(self, query: str) -> Tuple[bool, str]:
        """
        Detects if query asks about a fake or unknown drink name that does not exist in the manual.
        e.g., 'กาแฟอู๋ชิโน่', 'กาแฟไข่ดาว', 'กาแฟสายรุ้ง'
        """
        q_lower = query.lower()
        match = re.search(r'กาแฟ([ก-๙a-zA-Z]+)', q_lower)
        if match:
            drink_candidate = match.group(0).strip()
            # Strip common question suffix words
            for suffix in ["ไหม", "มั้ย", "หรือเปล่า", "บ้าง", "คืออะไร", "ทำยังไง", "สูตร"]:
                if drink_candidate.endswith(suffix) and len(drink_candidate) > len(suffix) + 4:
                    drink_candidate = drink_candidate[:-len(suffix)].strip()
            # If candidate contains any recognized valid manual drink keyword, it's ok
            if any(valid in drink_candidate for valid in VALID_MANUAL_DRINKS):
                return False, ""
            return True, drink_candidate
        return False, ""

    def validate_retrieval(self, contexts: List[Dict[str, Any]], query: str = "") -> Tuple[bool, str]:
        """
        Pre-generation guardrail:
        Checks if query is prompt injection, out of domain, or retrieved documents have insufficient semantic confidence.
        Returns (is_valid, message).
        """
        if query:
            if self.is_prompt_injection(query):
                return False, self.fallback_msg

            if self.is_out_of_domain_query(query):
                return False, self.fallback_msg

            # Check for fabricated drink name
            is_fake, fake_name = self.is_fabricated_drink_query(query)
            if is_fake:
                return False, (
                    f"ขออภัยครับ ในคู่มือประกอบการฝึกอบรมหลักสูตรบาริสต้ามืออาชีพ ไม่มีระบุข้อมูลเกี่ยวกับ \"{fake_name}\" ครับ "
                    f"ในคู่มือจะมีสูตรเครื่องดื่มมาตรฐาน 13 เมนู เช่น เอสเพรสโซ่, อเมริกาโน่, ลาเต้, คาปูชิโน่, มอคค่า, "
                    f"กาแฟส้ม, กาแฟพีช, ลาเต้มิ้นท์ และกาแฟน้ำผึ้งมะนาวครับ"
                )

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

        for ch_term, th_term in CHINESE_TERMS_MAP.items():
            text = text.replace(ch_term, th_term)

        for ch_punct, std_punct in CHINESE_PUNCTUATION_MAP.items():
            text = text.replace(ch_punct, std_punct)

        text = re.sub(r'[\u4e00-\u9fff]', '', text)
        text = re.sub(r'^\s*[-*•]\s*\*\*\(?\s*\)?\*\*[,.\s]*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*[-*•]\s*\*{2,4}[,.\s]*$', '', text, flags=re.MULTILINE)
        text = re.sub(r'^\s*[-*•]\s*[,.\s]+$', '', text, flags=re.MULTILINE)

        text = re.sub(r'[ \t]+', ' ', text)
        text = re.sub(r'\n{3,}', '\n\n', text)
        return text

    def sanitize_ocr_typos(self, text: str) -> str:
        """Corrects PDF OCR extraction typos and domain terminology."""
        if not text:
            return ""

        cleaned = text
        cleaned = re.sub(r'\(?\s*90\s*[-–]?\s*100\s*มิลลิแปร?์?\s*\)?', '(9-10 บาร์)', cleaned)
        cleaned = re.sub(r'มิลลิแปร?์', 'บาร์', cleaned)
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
        cleaned = re.sub(r'^(?:ข้อมูลที่\s*\d+\s*\|\s*หน้า\s*\d+\s*\|\s*หัวข้อ:[^\n]*\n*)+', '', cleaned)
        cleaned = re.sub(r'^(?:\[?(?:ข้อมูลที่|เอกสารอ้างอิงลำดับที่|เอกสารอ้างอิง)\s*\d*[^\]\n]*\]?:?\s*\n*)+', '', cleaned)
        cleaned = re.sub(r'^(?:>\s*\[?[^\]\n]+\]?\s*\n*)+', '', cleaned)
        return cleaned.strip()

    def validate_generation(self, query: str, answer: str, contexts: List[Dict[str, Any]]) -> str:
        """
        Post-generation guardrail:
        Ensures response respects boundaries, strips Chinese leakage, removes context tags,
        blocks code blocks/programming artifacts, and intercepts hallucinations.
        """
        if not answer or len(answer.strip()) < 5:
            return self.fallback_msg

        # If LLM triggered fallback text or acknowledged out-of-manual query
        fallback_indicators = [
            "ไม่มีระบุในคู่มือ",
            "ไม่สามารถให้คำตอบนอกเหนือจากเอกสาร",
            "ไม่มีข้อมูลในคู่มือ",
            "ไม่ได้ให้ข้อมูลเกี่ยวกับ",
            "ขออภัยสำหรับความสับสน แต่เอกสารที่คุณอ้างอิงไม่มีข้อมูล"
        ]
        if any(ind in answer for ind in fallback_indicators):
            return self.fallback_msg

        if self.is_prompt_injection(query):
            return self.fallback_msg

        if self.is_out_of_domain_query(query):
            return self.fallback_msg

        # Prevent prompt injection leaking in answer text
        ans_lower = answer.lower()
        if any(kw in ans_lower for kw in ["system instructions", "system instruction", "chunking id", "admin override", "โหมดบำรุงรักษา", "ไปป์ไลน์ rag"]):
            return self.fallback_msg

        # Check for fake drink name
        is_fake, fake_name = self.is_fabricated_drink_query(query)
        if is_fake:
            return (
                f"ขออภัยครับ ในคู่มือประกอบการฝึกอบรมหลักสูตรบาริสต้ามืออาชีพ ไม่มีระบุข้อมูลเกี่ยวกับ \"{fake_name}\" ครับ "
                f"ในคู่มือจะมีสูตรเครื่องดื่มมาตรฐาน 13 เมนู เช่น เอสเพรสโซ่, อเมริกาโน่, ลาเต้, คาปูชิโน่, มอคค่า, "
                f"กาแฟส้ม, กาแฟพีช, ลาเต้มิ้นท์ และกาแฟน้ำผึ้งมะนาวครับ"
            )

        # STRICT CODE BAN: If answer contains code blocks or class definitions, reject as fallback
        if "```" in answer or "class " in answer or "def __init__" in answer or "print(" in answer:
            return self.fallback_msg

        # If model hallucinated by pivoting away from missing info (e.g. pivoting kratom boiling to water boiling)
        pivot_indicators = [
            "สำหรับวิธีการต้มน้ำสำหรับ",
            "ดังนั้นผมจะสร้างโค้ด",
            "ผมจะสร้างโค้ด",
            "คัพวัชชิโน่"
        ]
        if any(p in answer for p in pivot_indicators):
            return self.fallback_msg

        # 1. Sanitize Chinese tokens and punctuation
        cleaned = self.sanitize_chinese(answer)

        # 2. Sanitize OCR typos and units
        cleaned = self.sanitize_ocr_typos(cleaned)

        # 3. Strip any accidental context header tags echoed by the LLM
        cleaned = self.strip_context_markers(cleaned)

        return cleaned.strip()
