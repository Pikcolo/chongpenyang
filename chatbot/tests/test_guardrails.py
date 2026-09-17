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

if __name__ == "__main__":
    unittest.main()
