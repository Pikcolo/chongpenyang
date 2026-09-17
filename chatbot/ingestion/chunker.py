"""
Advanced Semantic and Parent-Document Chunking module.
Generates small granular Child Chunks (for high-precision Dense/BM25 retrieval)
linked to comprehensive Parent Chunks (for high-fidelity LLM synthesis).
Preserves tabular structures and rich metadata.
"""

from typing import List, Dict, Any
from langchain_core.documents import Document
from chatbot.ingestion.metadata_extractor import detect_topic

class AdvancedChunker:
    """
    Implements Parent-Document Retriever chunking with semantic boundaries
    and layout/table preservation.
    """

    def __init__(
        self,
        child_chunk_size: int = 220,
        child_overlap: int = 40,
        parent_chunk_size: int = 750
    ):
        self.child_chunk_size = child_chunk_size
        self.child_overlap = child_overlap
        self.parent_chunk_size = parent_chunk_size

    def create_chunks(self, pages_data: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Processes parsed pages into Parent Documents and Child Documents.
        Returns:
            {
                "parents": List[Document],
                "children": List[Document]
            }
        """
        parent_docs: List[Document] = []
        child_docs: List[Document] = []
        parent_id_counter = 1
        child_id_counter = 1

        for page in pages_data:
            page_no = page["page_number"]
            page_text = page["text"]
            tables = page.get("tables", [])
            
            # Combine page text with tables if any
            combined_page_content = page_text
            if tables:
                table_block = "\n\n[ตารางข้อมูลโครงสร้าง]:\n" + "\n\n".join(tables)
                combined_page_content = f"{page_text}\n{table_block}".strip()

            if not combined_page_content or len(combined_page_content) < 10:
                continue

            topic_info = detect_topic(combined_page_content, page_no=page_no)
            topic_title = topic_info["topic_title"]
            doc_name = topic_info["document_name"]
            module_id = topic_info.get("module_id", "MOD_01")

            # Create Parent Document for this page or logical section
            parent_id = f"parent_{parent_id_counter:04d}"
            parent_id_counter += 1

            parent_meta = {
                "parent_id": parent_id,
                "page": page_no,
                "module_id": module_id,
                "topic_title": topic_title,
                "topic_id": topic_info["topic_id"],
                "document_name": doc_name,
                "has_table": bool(tables),
                "type": "parent"
            }
            parent_doc = Document(
                page_content=combined_page_content,
                metadata=parent_meta
            )
            parent_docs.append(parent_doc)

            # 1. If page contains tables, create dedicated Child Chunk for each table
            for t_idx, table_md in enumerate(tables):
                child_id = f"child_{child_id_counter:04d}"
                child_id_counter += 1
                table_content = f"[ตารางความรู้]:\n{table_md}"
                child_docs.append(
                    Document(
                        page_content=table_content,
                        metadata={
                            "child_id": child_id,
                            "parent_id": parent_id,
                            "parent_content": combined_page_content,
                            "page": page_no,
                            "module_id": module_id,
                            "topic_title": topic_title,
                            "topic_id": topic_info["topic_id"],
                            "document_name": doc_name,
                            "is_table": True,
                            "type": "child"
                        }
                    )
                )

            # 2. Split page text into Child Chunks using sliding window
            paragraphs = [p.strip() for p in page_text.split("\n") if p.strip()]
            if not paragraphs:
                continue

            current_tokens = []
            for para in paragraphs:
                current_tokens.append(para)
                combined_text = "\n".join(current_tokens)
                
                # Approximate word/character length threshold for child chunk
                if len(combined_text) >= self.child_chunk_size:
                    child_id = f"child_{child_id_counter:04d}"
                    child_id_counter += 1
                    child_docs.append(
                        Document(
                            page_content=combined_text,
                            metadata={
                                "child_id": child_id,
                                "parent_id": parent_id,
                                "parent_content": combined_page_content,
                                "page": page_no,
                                "module_id": module_id,
                                "topic_title": topic_title,
                                "topic_id": topic_info["topic_id"],
                                "document_name": doc_name,
                                "is_table": False,
                                "type": "child"
                            }
                        )
                    )
                    # Keep overlap for sliding window
                    overlap_chars = 0
                    kept_tokens = []
                    for t in reversed(current_tokens):
                        if overlap_chars + len(t) <= self.child_overlap:
                            kept_tokens.insert(0, t)
                            overlap_chars += len(t)
                        else:
                            break
                    current_tokens = kept_tokens

            # Any remaining text as final child chunk
            if current_tokens:
                remaining_text = "\n".join(current_tokens).strip()
                if remaining_text and len(remaining_text) > 20:
                    child_id = f"child_{child_id_counter:04d}"
                    child_id_counter += 1
                    child_docs.append(
                        Document(
                            page_content=remaining_text,
                            metadata={
                                "child_id": child_id,
                                "parent_id": parent_id,
                                "parent_content": combined_page_content,
                                "page": page_no,
                                "module_id": module_id,
                                "topic_title": topic_title,
                                "topic_id": topic_info["topic_id"],
                                "document_name": doc_name,
                                "is_table": False,
                                "type": "child"
                            }
                        )
                    )

        return {
            "parents": parent_docs,
            "children": child_docs
        }
