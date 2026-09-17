"""
Interactive CLI Chat Testbench for SmartDoc Barista Hybrid RAG.
Provides real-time inspection of dynamic top-k, candidate scores, and citations.
"""

import sys
import pickle
from pathlib import Path

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from chatbot.config import settings
from chatbot.retrieval.vector_store import VectorStoreManager
from chatbot.retrieval.bm25_retriever import BM25Retriever
from chatbot.retrieval.reranker import CrossEncoderReranker
from chatbot.retrieval.dynamic_retriever import DynamicHybridRetriever
from chatbot.generation.guardrails import GuardrailManager
from chatbot.generation.rag_chain import BaristaRAGChain

def main():
    print("=" * 70)
    print("☕ SMARTDOC BARISTA HYBRID RAG - INTERACTIVE CLI TESTBENCH")
    print(f"🤖 LLM Model: {settings.OLLAMA_MODEL} | Vector Store: {settings.VECTOR_STORE_TYPE.upper()}")
    print("พิมพ์คำถามเกี่ยวกับบาริสต้า หรือพิมพ์ 'exit' เพื่อออกจากโปรแกรม")
    print("=" * 70)

    # 1. Initialize Components
    print("⏳ กำลังโหลด RAG Engine และดัชนี...")
    vector_mgr = VectorStoreManager(store_type=settings.VECTOR_STORE_TYPE)
    if not vector_mgr.load_existing():
        print("❌ ไม่พบ Vector Index กรุณารัน: python -m chatbot.ingestion.build_index ก่อน")
        return

    cache_path = Path(settings.CHROMA_PATH).parent / "documents_cache.pkl"
    if not cache_path.exists():
        print("❌ ไม่พบ Cached Documents กรุณารัน build_index ก่อน")
        return

    with open(cache_path, "rb") as f:
        child_docs = pickle.load(f)

    bm25 = BM25Retriever(child_docs)
    reranker = CrossEncoderReranker(settings.RERANKER_MODEL) if settings.RERANKER_ENABLED else None
    retriever = DynamicHybridRetriever(vector_mgr, bm25, reranker)
    guardrails = GuardrailManager()
    rag_chain = BaristaRAGChain(retriever, guardrails)

    print("✅ ระบบพร้อมใช้งาน!\n")

    session_id = "cli_session"

    while True:
        try:
            user_input = input("\n👤 คุณ: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ["exit", "quit", "q"]:
                print("👋 ขอบคุณที่ใช้งาน SmartDoc Barista AI ครับ!")
                break
            if user_input.lower() == "clear":
                print("🧹 ระบบทำงานในโหมด Stateless (ไม่เก็บประวัติการสนทนาอยู่แล้วครับ)")
                continue

            print("🔍 กำลังค้นหาข้อมูลและประมวลผลคำตอบ...")
            output = rag_chain.answer_question(user_input, session_id=session_id)

            print("\n" + "-" * 70)
            print(f"📊 [Dynamic Top-k: {output['dynamic_k']} | Retrieved Chunks: {len(output['contexts'])}]")
            if output["guardrail_triggered"]:
                print("🛡️ [Guardrail Triggered: Zero Hallucination Fallback]")
            print("-" * 70)
            print(f"🤖 บาริสต้า AI:\n{output['answer']}")
            print("-" * 70)

        except (KeyboardInterrupt, EOFError):
            print("\n👋 สิ้นสุดการสนทนา")
            break

if __name__ == "__main__":
    main()
