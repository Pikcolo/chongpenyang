"""
PDF Parser supporting text, layout, and table extraction via pdfplumber.
Preserves table relationships as Markdown tables and extracts page-level metadata.
"""

import os
from typing import List, Dict, Any
import pdfplumber

from chatbot.ingestion.text_cleaner import clean_thai_text, filter_header_footer_lines

class PDFParser:
    """Extracts structured content, text, and tables from PDF manuals."""

    def __init__(self, pdf_path: str):
        if not os.path.exists(pdf_path):
            raise FileNotFoundError(f"PDF document not found at: {pdf_path}")
        self.pdf_path = pdf_path

    def table_to_markdown(self, table: List[List[Any]]) -> str:
        """Converts raw table cell matrix into clean Markdown table format."""
        if not table or len(table) < 2:
            return ""

        cleaned_table = []
        for row in table:
            cleaned_row = [clean_thai_text(str(cell or "").replace("\n", " ").strip()) for cell in row]
            if any(cleaned_row):
                cleaned_table.append(cleaned_row)

        if not cleaned_table:
            return ""

        # Normalize column count across all rows
        max_cols = max(len(r) for r in cleaned_table)
        for r in cleaned_table:
            while len(r) < max_cols:
                r.append("")

        header = cleaned_table[0]
        separator = ["---"] * max_cols
        rows = cleaned_table[1:]

        md_lines = [
            "| " + " | ".join(header) + " |",
            "| " + " | ".join(separator) + " |"
        ]
        for row in rows:
            md_lines.append("| " + " | ".join(row) + " |")

        return "\n".join(md_lines)

    def extract_pages(self) -> List[Dict[str, Any]]:
        """
        Parses all pages in the PDF document.
        Returns a list of page dicts containing:
          - page_number: int (1-based)
          - text: str (cleaned body text)
          - tables: list of str (markdown tables)
          - raw_lines: list of str
        """
        pages_data = []

        with pdfplumber.open(self.pdf_path) as pdf:
            total_pages = len(pdf.pages)
            for idx, page in enumerate(pdf.pages, start=1):
                raw_text = page.extract_text(layout=False) or ""
                cleaned_raw = clean_thai_text(raw_text)
                
                # Extract tables if any
                tables_md = []
                try:
                    tables = page.extract_tables()
                    for t in tables:
                        md_table = self.table_to_markdown(t)
                        if md_table:
                            tables_md.append(md_table)
                except Exception:
                    pass

                # Clean lines & remove repetitive headers
                split_lines = cleaned_raw.split("\n")
                filtered_lines = filter_header_footer_lines(split_lines)
                page_text = "\n".join(filtered_lines)

                pages_data.append({
                    "page_number": idx,
                    "total_pages": total_pages,
                    "text": page_text,
                    "tables": tables_md,
                    "raw_lines": filtered_lines
                })

        return pages_data
