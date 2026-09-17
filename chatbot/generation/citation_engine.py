"""
Citation and Source Reference Engine.
Formats structured metadata, topics, pages, and excerpts for transparent evidence.
"""

from typing import List, Dict, Any

class CitationEngine:
    """Extracts, formats, and renders citations from retrieved contexts."""

    @staticmethod
    def extract_citations(contexts: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Extracts deduplicated structured citations from retrieved chunks."""
        citations = []
        seen = set()

        for c in contexts:
            page = c.get("page", 1)
            topic = c.get("topic_title", "ความรู้ทั่วไปเกี่ยวกับกาแฟ")
            doc_name = c.get("document_name", "คู่มือประกอบการฝึกอบรม หลักสูตร: บาริสต้ามืออาชีพ")
            key = (page, topic)
            if key in seen:
                continue
            seen.add(key)

            snippet = c.get("content", "").strip()
            # Clean snippet for preview (first 120 chars)
            first_line = snippet.split("\n")[0] if snippet else ""
            preview = (first_line[:120] + "...") if len(first_line) > 120 else first_line

            citations.append({
                "page": page,
                "topic": topic,
                "document": doc_name,
                "preview": preview,
                "reference_link": f"documents.pdf#page={page}"
            })

        return citations

    @classmethod
    def format_markdown_footer(cls, citations: List[Dict[str, Any]]) -> str:
        """Formats citations as an elegant Markdown footnote."""
        if not citations:
            return ""

        lines = ["\n\n📚 **แหล่งอ้างอิงข้อมูล (Citations & Sources):**"]
        for cite in citations:
            page = cite["page"]
            topic = cite["topic"]
            doc = cite["document"]
            lines.append(f"• 📖 **หน้า {page}** — *{topic}* ({doc})")

        return "\n".join(lines)
