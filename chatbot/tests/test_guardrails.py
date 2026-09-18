import unittest
from chatbot.generation.guardrails import GuardrailManager
from chatbot.generation.citation_engine import CitationEngine

class TestGuardrailsAndCitations(unittest.TestCase):

    def setUp(self):
        self.guardrail = GuardrailManager(min_threshold=0.25)

    def test_guardrail_insufficient_similarity(self):
        # Very low score below threshold 0.25
        contexts = [{"content": "...", "score": 0.10}]
        valid, msg = self.guardrail.validate_retrieval(contexts)
        self.assertFalse(valid)
        self.assertIn("ไม่มีระบุในคู่มือ", msg)

    def test_guardrail_sufficient_similarity(self):
        contexts = [{"content": "...", "score": 0.65}]
        valid, msg = self.guardrail.validate_retrieval(contexts)
        self.assertTrue(valid)

    def test_citation_extraction(self):
        contexts = [
            {
                "page": 24,
                "topic_title": "การสกัดเอสเพรสโซ่",
                "document_name": "คู่มือบาริสต้า",
                "content": "Perfect shot ต้องสกัด 20-30 วินาที"
            },
            {
                "page": 24,  # Duplicate page & topic should be deduplicated
                "topic_title": "การสกัดเอสเพรสโซ่",
                "document_name": "คู่มือบาริสต้า",
                "content": "แรงดัน 9 บาร์"
            },
            {
                "page": 35,
                "topic_title": "สูตรลาเต้ร้อน",
                "document_name": "คู่มือบาริสต้า",
                "content": "ใช้นมสตีม 4-5 ออนซ์"
            }
        ]
        citations = CitationEngine.extract_citations(contexts)
        self.assertEqual(len(citations), 2)
        self.assertEqual(citations[0]["page"], 24)
        self.assertEqual(citations[1]["page"], 35)

        footer = CitationEngine.format_markdown_footer(citations)
        self.assertIn("หน้า 24", footer)
        self.assertIn("หน้า 35", footer)

    def test_typo_sanitization(self):
        dirty_text = "ชงเสร็จแล้ว พรอ้ มเสิรฟ์ ในแก้วเสริฟ พร้อมตกแต่งสวยงาม สกัดช็อค 90 มิลลิแปร"
        cleaned = self.guardrail.sanitize_ocr_typos(dirty_text)
        self.assertIn("พร้อมเสิร์ฟ", cleaned)
        self.assertIn("แก้วเสิร์ฟ", cleaned)
        self.assertIn("สกัดช็อต", cleaned)
        self.assertIn("บาร์", cleaned)
        self.assertNotIn("เสิรฟ์", cleaned)
        self.assertNotIn("เสริฟ", cleaned)
        self.assertNotIn("พรอ้ ม", cleaned)
        self.assertNotIn("สกัดช็อค", cleaned)

        orange_dirty = "ส่วนผสม: 1. น้ำ สมั 2. ถว้ ยตวง 3. ซอ้ นตกั 4. กาตม้ นน้ำรอ้ น 5. ถงุ 6. อุปกรณท์ 7. ใหเ้ขา้ กนั 8. เบอร์บั เบอรบ์ดใหล้ ะเอียด"
        orange_cleaned = self.guardrail.sanitize_ocr_typos(orange_dirty)
        self.assertIn("น้ำส้ม", orange_cleaned)
        self.assertIn("ถ้วยตวง", orange_cleaned)
        self.assertIn("ช้อนตัก", orange_cleaned)
        self.assertIn("กาต้มน้ำร้อน", orange_cleaned)
        self.assertIn("ถุง", orange_cleaned)
        self.assertIn("อุปกรณ์ที่", orange_cleaned)
        self.assertIn("ให้เข้ากัน", orange_cleaned)
        self.assertIn("เบอร์บดให้ละเอียด", orange_cleaned)
        self.assertNotIn("น้ำ สมั", orange_cleaned)
        self.assertNotIn("ถว้ ย", orange_cleaned)
        self.assertNotIn("ซอ้ น", orange_cleaned)

    def test_out_of_domain_python(self):
        query = "ยกตัวอย่างกาแฟด้วยโค้ด python"
        valid, msg = self.guardrail.validate_retrieval([{"content": "กาแฟ", "score": 0.8}], query=query)
        self.assertFalse(valid)
        self.assertIn("ไม่มีระบุในคู่มือ", msg)

if __name__ == "__main__":
    unittest.main()
