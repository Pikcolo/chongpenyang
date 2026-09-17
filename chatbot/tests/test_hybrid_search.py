import unittest
from langchain_core.documents import Document
from chatbot.retrieval.bm25_retriever import BM25Retriever
from chatbot.retrieval.fusion import reciprocal_rank_fusion, relative_score_fusion

class TestHybridSearch(unittest.TestCase):

    def setUp(self):
        self.doc1 = Document(
            page_content="การสกัดกาแฟเอสเพรสโซ่ใช้น้ำอุณหภูมิ 90-95 องศาเซลเซียส",
            metadata={"child_id": "c1", "page": 23}
        )
        self.doc2 = Document(
            page_content="ระดับการคั่วกาแฟ Agtron Scale สำหรับคั่วอ่อนคือ 75-95",
            metadata={"child_id": "c2", "page": 18}
        )
        self.doc3 = Document(
            page_content="สูตรการทำลาเต้ร้อน ใช้เอสเพรสโซ่ผสมนมร้อนที่สตีม",
            metadata={"child_id": "c3", "page": 35}
        )
        self.docs = [self.doc1, self.doc2, self.doc3]

    def test_bm25_search(self):
        retriever = BM25Retriever(self.docs)
        results = retriever.search("Agtron คั่วอ่อน", top_k=2)
        self.assertGreaterEqual(len(results), 1)
        self.assertEqual(results[0][0].metadata["child_id"], "c2")

    def test_rrf_fusion(self):
        dense_results = [(self.doc1, 0.9), (self.doc2, 0.7)]
        sparse_results = [(self.doc2, 4.5), (self.doc3, 2.1)]
        fused = reciprocal_rank_fusion(dense_results, sparse_results, k=60)
        self.assertEqual(len(fused), 3)
        # Doc2 appeared in both lists so it should rank highly
        fused_ids = [d.metadata["child_id"] for d, _ in fused]
        self.assertIn("c2", fused_ids[:2])

    def test_relative_score_fusion(self):
        dense_results = [(self.doc1, 0.9), (self.doc2, 0.7)]
        sparse_results = [(self.doc2, 4.5), (self.doc3, 2.1)]
        fused = relative_score_fusion(dense_results, sparse_results, dense_weight=0.5, sparse_weight=0.5)
        self.assertEqual(len(fused), 3)

if __name__ == "__main__":
    unittest.main()
