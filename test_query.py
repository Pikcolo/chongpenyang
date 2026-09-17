import pickle
import sys
from pathlib import Path
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from chatbot.config import settings
from chatbot.retrieval.vector_store import VectorStoreManager
from chatbot.retrieval.bm25_retriever import BM25Retriever
from chatbot.retrieval.dynamic_retriever import DynamicHybridRetriever
from chatbot.retrieval.reranker import CrossEncoderReranker
from chatbot.generation.rag_chain import BaristaRAGChain

print(f"Testing with model: {settings.OLLAMA_MODEL}")
vm = VectorStoreManager(settings.VECTOR_STORE_TYPE)
vm.load_existing()
cache_path = Path(settings.CHROMA_PATH).parent / "documents_cache.pkl"
with open(cache_path, "rb") as f:
    docs = pickle.load(f)
bm = BM25Retriever(docs)
reranker = CrossEncoderReranker(settings.RERANKER_MODEL) if settings.RERANKER_ENABLED else None
dr = DynamicHybridRetriever(vm, bm, reranker)
chain = BaristaRAGChain(dr)

queries = [
    "สวัสดีครับ",
    "อุณหภูมิน้ำและแรงดันในการสกัดเอสเพรสโซ่ที่ถูกต้องคือเท่าไร?"
]

for q in queries:
    print("\n" + "="*50)
    print(f"QUERY: {q}")
    res = chain.answer_question(q, session_id="test_session")
    print(f"ANSWER:\n{res['answer']}")
    print(f"CITATIONS: {res['citations']}")
