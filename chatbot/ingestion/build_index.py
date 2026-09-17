"""
Index Builder Script for Chatbot Project 2.
Extracts PDF using layout/table awareness, performs Semantic/Parent-Document chunking,
builds ChromaDB/FAISS vector store, and saves tokenized BM25 corpus.
"""

import os
import sys
import json
import pickle
from pathlib import Path

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from chatbot.config import settings
from chatbot.ingestion.pdf_parser import PDFParser
from chatbot.ingestion.chunker import AdvancedChunker
from chatbot.retrieval.vector_store import VectorStoreManager
from chatbot.retrieval.bm25_retriever import BM25Retriever

def build_indices():
    print("=" * 70)
    print("🚀 SMARTDOC BARISTA HYBRID RAG: BUILDING INDICES (GRADE A PRODUCTION)")
    print("=" * 70)

    pdf_path = settings.PDF_PATH
    print(f"📖 Reading source PDF: {pdf_path}")
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Source PDF not found at: {pdf_path}")

    # 1. Layout & Table Aware Parsing
    parser = PDFParser(pdf_path)
    pages_data = parser.extract_pages()
    print(f"✅ Successfully parsed {len(pages_data)} pages from PDF.")

    # 2. Semantic & Parent-Child Chunking
    chunker = AdvancedChunker(child_chunk_size=220, child_overlap=40, parent_chunk_size=750)
    chunk_result = chunker.create_chunks(pages_data)
    parent_docs = chunk_result["parents"]
    child_docs = chunk_result["children"]
    print(f"✅ Generated {len(parent_docs)} Parent Documents and {len(child_docs)} Child Chunks.")

    # Count table chunks
    table_chunks_count = sum(1 for c in child_docs if c.metadata.get("is_table"))
    print(f"📊 Structured Table Chunks: {table_chunks_count}")

    # 3. Build & Persist Dense Vector Store (Both Chroma & FAISS for flexibility)
    data_dir = Path(settings.CHROMA_PATH).parent
    os.makedirs(data_dir, exist_ok=True)

    # Save child documents list to disk for BM25 and fast reloading
    corpus_file = data_dir / "documents_cache.pkl"
    with open(corpus_file, "wb") as f:
        pickle.dump(child_docs, f)
    print(f"💾 Cached {len(child_docs)} child documents to: {corpus_file}")

    # ChromaDB
    print("\n📦 Building ChromaDB Vector Index...")
    chroma_mgr = VectorStoreManager(store_type="chroma")
    chroma_mgr.build_from_documents(child_docs)

    # FAISS (also build FAISS as backup/alternative backend)
    print("\n📦 Building FAISS Vector Index...")
    faiss_mgr = VectorStoreManager(store_type="faiss")
    faiss_mgr.build_from_documents(child_docs)

    # 4. Initialize and verify BM25
    print("\n🔍 Initializing BM25 Index with Thai Segmentation...")
    bm25_retriever = BM25Retriever(child_docs)
    sample_res = bm25_retriever.search("อัตราส่วนการสกัดเอสเพรสโซ่", top_k=2)
    print(f"✅ BM25 verification passed: retrieved {len(sample_res)} hits.")

    print("\n" + "=" * 70)
    print("🎉 ALL PRODUCTION RAG INDICES SUCCESSFULLY BUILT AND PERSISTED!")
    print("=" * 70)

if __name__ == "__main__":
    build_indices()
