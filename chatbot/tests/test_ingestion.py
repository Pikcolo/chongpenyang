import unittest
from chatbot.ingestion.text_cleaner import clean_thai_text, filter_header_footer_lines
from chatbot.ingestion.metadata_extractor import detect_topic
from chatbot.ingestion.chunker import AdvancedChunker

class TestIngestion(unittest.TestCase):

    def test_thai_text_cleaner(self):
        sample = "กำแฟ ลำเต้ น ้ำ อเมริกำโน่"
        cleaned = clean_thai_text(sample)
        self.assertEqual(cleaned, "กาแฟ ลาเต้ น้ำ อเมริกาโน่")

    def test_header_footer_filter(self):
        lines = [
            "ใบข้อมูลที่ 1",
            "หลักสูตร :บาริสต้ามืออาชีพ",
            "การสกัดกาแฟเอสเพรสโซ่",
            "หน้า 23"
        ]
        filtered = filter_header_footer_lines(lines)
        self.assertEqual(len(filtered), 1)
        self.assertEqual(filtered[0], "การสกัดกาแฟเอสเพรสโซ่")

    def test_topic_detection(self):
        text = "การคั่วกาแฟระดับคั่วอ่อน Light Roast มีค่า Agtron 75-95"
        topic_info = detect_topic(text)
        self.assertIn(topic_info["topic_id"], ["mod_01", "roasting"])
        self.assertIn("คั่ว", topic_info["topic_title"])

    def test_advanced_chunker(self):
        chunker = AdvancedChunker(child_chunk_size=100, child_overlap=20)
        pages_data = [{
            "page_number": 1,
            "text": "พฤกษศาสตร์กาแฟ สายพันธุ์อาราบิก้าและโรบัสต้ามีข้อแตกต่างกันในเรื่องของความสูงและคาเฟอีน\n" * 5,
            "tables": []
        }]
        res = chunker.create_chunks(pages_data)
        self.assertGreaterEqual(len(res["parents"]), 1)
        self.assertGreaterEqual(len(res["children"]), 1)
        # Check child metadata has parent_id
        self.assertTrue("parent_id" in res["children"][0].metadata)

if __name__ == "__main__":
    unittest.main()
