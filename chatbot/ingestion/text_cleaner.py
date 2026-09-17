"""
Text cleaning and normalization module for Thai PDF documents.
Handles OCR typos, ligature glitched characters, floating vowels,
and removes repetitive headers/footers.
"""

import re
from typing import List

# Common OCR / PDF extraction glitched words in Thai barista manuals
THAI_TYPO_MAPPING = {
    '\ufffd': 'า',
    'กำแฟ': 'กาแฟ',
    'ลำเต้': 'ลาเต้',
    'อเมริกำโน่': 'อเมริกาโน่',
    'น ้ำ': 'น้ำ',
    'น ้าร้อน': 'น้ำร้อน',
    'น ้าผึ้ง': 'น้ำผึ้ง',
    'น ้ามะนาว': 'น้ำมะนาว',
    'น ้าส้ม': 'น้ำส้ม',
    'น ้าสัม': 'น้ำส้ม',
    'น ้าแข็ง': 'น้ำแข็ง',
    'น ้าตาล': 'น้ำตาล',
    'น ้ามัน': 'น้ำมัน',
    'น ้าเชื่อม': 'น้ำเชื่อม',
    'น ้าเย็น': 'น้ำเย็น',
    'น ้าอุ่น': 'น้ำอุ่น',
    'ถวงตวง': 'ถ้วยตวง',
    'ใส้ก้านชง': 'ใส่ก้านชง',
    'แทมปักาแฟ': 'แทมป์กาแฟ',
    'ซ้อนตักกาแฟ': 'ช้อนตักกาแฟ',
    'สกัดช็อค': 'สกัดช็อต',
    'เรอสกัด': 'รอสกัด',
    'เอสเพรสโช่': 'เอสเพรสโซ่',
    'เอสเพรสโช': 'เอสเพรสโซ่',
    'เฮสเปรสโซ่': 'เอสเพรสโซ่',
    'มอคค่ำ': 'มอคค่า',
    'มัคคิอำโต้': 'มัคคิอาโต้',
    'คำปูชิโน่': 'คาปูชิโน่',
    'ชำเขียว': 'ชาเขียว',
    'ชำไทย': 'ชาไทย',
    'อำรำบิก้ำ': 'อาราบิก้า',
    'โรบัสต้ำ': 'โรบัสต้า',
    'ฟองนมเนียนนุ่ม': 'ฟองนมเนียนนุ่ม',
}

REPETITIVE_HEADER_FOOTER_PATTERNS = [
    r'ใบข้อมูล\s*(?:ที่\s*\d+)?',
    r'หลักสูตร\s*:\s*บาริสต้ามืออาชีพ',
    r'หัวข้อวิชา\s*:\s*.*',
    r'งานย่อยที่\s*:\s*\d+.*',
    r'เวลา\s*\d+\s*ชั่วโมง',
    r'หน้า\s*\d+\s*(?:จาก\s*\d+)?',
    r'^\s*\d+\s*$',  # Standalone page numbers
]

def clean_thai_text(text: str) -> str:
    """Cleans Thai PDF extraction artifacts, fixes broken diacritics and ligatures."""
    if not text:
        return ""

    # Replace known font encoding / ligature bugs
    for bad, good in THAI_TYPO_MAPPING.items():
        text = text.replace(bad, good)

    # Fix space between sara am or broken tone marks
    text = re.sub(r'([ก-ฮ])\s+ำ', r'\1ำ', text)
    text = re.sub(r'([ก-ฮ])\s+([่้๊๋])', r'\1\2', text)
    text = re.sub(r'([่้๊๋])\s+([ิีึืุู])', r'\2\1', text)

    # Normalize multiple whitespace characters except newline
    text = re.sub(r'[ \t]+', ' ', text)
    
    # Remove null bytes and strange unprintable characters
    text = re.sub(r'[\x00-\x08\x0b\x0c\x0e-\x1f\x7f]', '', text)

    return text.strip()

def filter_header_footer_lines(lines: List[str]) -> List[str]:
    """Filters out recurring boilerplates, headers, footers, and page counters."""
    cleaned_lines = []
    for line in lines:
        stripped = line.strip()
        if not stripped or len(stripped) <= 1:
            continue

        # Check regex boilerplate patterns
        is_boilerplate = False
        for pattern in REPETITIVE_HEADER_FOOTER_PATTERNS:
            if re.search(pattern, stripped, re.IGNORECASE):
                is_boilerplate = True
                break
        
        if not is_boilerplate:
            cleaned_lines.append(stripped)

    return cleaned_lines
