"""
Index Builder Script for Chongpenyang Barista AI Hybrid RAG.
Extracts PDF using layout/table awareness, incorporates comprehensive curriculum knowledge,
performs Semantic/Parent-Document chunking, builds ChromaDB and FAISS vector stores,
and persists tokenized BM25 corpus.
"""

import os
import sys
import re
import pickle
from pathlib import Path
from typing import List, Tuple
from langchain_core.documents import Document

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from chatbot.config import settings
from chatbot.ingestion.pdf_parser import PDFParser
from chatbot.ingestion.chunker import AdvancedChunker
from chatbot.ingestion.text_cleaner import clean_thai_text
from chatbot.ingestion.metadata_extractor import detect_topic
from chatbot.retrieval.vector_store import VectorStoreManager
from chatbot.retrieval.bm25_retriever import BM25Retriever

def parse_curriculum_markdown(
    md_path: str,
    start_parent_id: int = 100,
    start_child_id: int = 1000
) -> Tuple[List[Document], List[Document]]:
    """
    Parses structured curriculum markdown into Parent Documents and Child Documents.
    Extracts explicit page metadata, topic titles, and granular subsections.
    """
    if not os.path.exists(md_path):
        print(f"⚠️ Note: Curriculum knowledge file not found at {md_path}")
        return [], []

    with open(md_path, "r", encoding="utf-8") as f:
        full_text = f.read()

    sections = re.split(r'\n(?=##\s+(?:MOD_\d+|หมวดที่))', full_text)
    parent_docs = []
    child_docs = []
    parent_id_counter = start_parent_id
    child_id_counter = start_child_id

    for sec in sections:
        sec = sec.strip()
        if not sec or not sec.startswith("## "):
            continue

        lines = sec.split("\n")
        header_line = lines[0].replace("## ", "").strip()
        body_lines = lines[1:]
        body_text = "\n".join(body_lines).strip()

        # Extract page number pattern: [หน้า 23-24 | ...] or [หน้า 40]
        page_no = 1
        page_match = re.search(r'\[หน้า\s*(\d+)(?:[-–]\d+)?\s*(?:\|.*?)?\]', body_text)
        if page_match:
            try:
                page_no = int(page_match.group(1))
            except ValueError:
                page_no = 1

        topic_info = detect_topic(sec, page_no=page_no)
        parent_id = f"parent_{parent_id_counter:04d}"
        parent_id_counter += 1

        parent_meta = {
            "parent_id": parent_id,
            "page": page_no,
            "module_id": topic_info.get("module_id", "MOD_01"),
            "topic_title": header_line,
            "topic_id": topic_info["topic_id"],
            "document_name": "คู่มือหลักสูตรบาริสต้ามืออาชีพ (Curriculum & SOP)",
            "has_table": False,
            "type": "parent"
        }
        parent_docs.append(Document(page_content=clean_thai_text(sec), metadata=parent_meta))

        # Split into granular child subsections by numbered items or subheadings
        subsections = re.split(r'\n(?=(?:###\s+|\d+\.\s+\*\*|[-*]\s+\*\*))', body_text)
        for sub in subsections:
            sub = sub.strip()
            if not sub or len(sub) < 30:
                continue

            sub_page = page_no
            sub_page_match = re.search(r'\[หน้า\s*(\d+)(?:[-–]\d+)?\s*(?:\|.*?)?\]', sub)
            if sub_page_match:
                try:
                    sub_page = int(sub_page_match.group(1))
                except ValueError:
                    pass

            child_id = f"child_{child_id_counter:04d}"
            child_id_counter += 1

            child_meta = {
                "child_id": child_id,
                "parent_id": parent_id,
                "parent_content": clean_thai_text(sec),
                "page": sub_page,
                "module_id": topic_info.get("module_id", "MOD_01"),
                "topic_title": header_line,
                "topic_id": topic_info["topic_id"],
                "document_name": "คู่มือหลักสูตรบาริสต้ามืออาชีพ (Curriculum & SOP)",
                "is_table": False,
                "type": "child"
            }
            child_docs.append(Document(page_content=clean_thai_text(sub), metadata=child_meta))

    return parent_docs, child_docs

def build_indices():
    print("=" * 75)
    print("🚀 CHONGPENYANG BARISTA HYBRID RAG: BUILDING INDICES (GRADE A PRODUCTION)")
    print("=" * 75)

    pdf_path = settings.PDF_PATH
    print(f"📖 Reading primary source PDF: {pdf_path}")
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"Source PDF not found at: {pdf_path}")

    # 1. Layout & Table Aware Parsing of PDF
    parser = PDFParser(pdf_path)
    pages_data = parser.extract_pages()
    print(f"✅ Successfully parsed {len(pages_data)} pages from PDF.")

    # 2. Semantic & Parent-Child Chunking of PDF
    chunker = AdvancedChunker(child_chunk_size=220, child_overlap=40, parent_chunk_size=750)
    chunk_result = chunker.create_chunks(pages_data)
    pdf_parents = chunk_result["parents"]
    pdf_children = chunk_result["children"]
    print(f"✅ Generated {len(pdf_parents)} Parent Docs and {len(pdf_children)} Child Chunks from PDF.")

    # 3. Ingest Supplementary Barista Knowledge & SOP
    curriculum_md_path = Path(settings.CHROMA_PATH).parent / "barista_curriculum_knowledge.md"
    curr_parents, curr_children = parse_curriculum_markdown(
        str(curriculum_md_path),
        start_parent_id=len(pdf_parents) + 1,
        start_child_id=len(pdf_children) + 1
    )
    print(f"✅ Generated {len(curr_parents)} Parent Docs and {len(curr_children)} Child Chunks from Curriculum Knowledge.")

    all_parents = pdf_parents + curr_parents
    all_children = pdf_children + curr_children
    print(f"📊 TOTAL CORPUS: {len(all_parents)} Parent Documents | {len(all_children)} Child Chunks.")

    # Count table chunks
    table_chunks_count = sum(1 for c in all_children if c.metadata.get("is_table"))
    print(f"📊 Structured Table Chunks: {table_chunks_count}")

    # 4. Cache Documents to Disk
    data_dir = Path(settings.CHROMA_PATH).parent
    os.makedirs(data_dir, exist_ok=True)
    corpus_file = data_dir / "documents_cache.pkl"
    with open(corpus_file, "wb") as f:
        pickle.dump(all_children, f)
    print(f"💾 Cached {len(all_children)} child documents to: {corpus_file}")

    # 5. Build & Persist Dense Vector Store (FAISS)
    if settings.VECTOR_STORE_TYPE == "faiss":
        print("\n📦 Building FAISS Vector Store (Primary Production Vector Store)...")
        faiss_mgr = VectorStoreManager(store_type="faiss")
        faiss_mgr.build_from_documents(all_children)
    else:
        print("\n📦 Building ChromaDB Vector Store...")
        chroma_mgr = VectorStoreManager(store_type="chroma")
        chroma_mgr.build_from_documents(all_children)

    # 6. Build & Persist BM25 Index
    print("\n🔍 Initializing BM25 Index with PyThaiNLP newmm segmentation...")
    bm25_retriever = BM25Retriever(all_children)
    
    bm25_index_file = data_dir / "bm25_index.pkl"
    with open(bm25_index_file, "wb") as f:
        pickle.dump(bm25_retriever, f)
    print(f"💾 Persisted BM25 retriever index to: {bm25_index_file}")

    # 7. Verification Tests
    test_queries = [
        "อุณหภูมิน้ำและแรงดันในการสกัดเอสเพรสโซ่",
        "Dirty Coffee",
        "Channeling คืออะไร",
        "First Crack Second Crack",
        "การ Backflush",
        "Bottomless Naked Portafilter"
    ]
    print("\n🔎 Running Index Verification Tests:")
    for tq in test_queries:
        hits = bm25_retriever.search(tq, top_k=2)
        top_page = hits[0][0].metadata.get("page") if hits else "None"
        print(f"  • Query '{tq}' -> {len(hits)} hits (Top Page: {top_page})")

    print("\n" + "=" * 75)
    print("🎉 ALL PRODUCTION RAG INDICES SUCCESSFULLY BUILT AND PERSISTED!")
    print("=" * 75)

if __name__ == "__main__":
    build_indices()
