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
    'ฟองนมเนียนนุ่ม': 'ฟองนมเนียนนุ่ม',
    'ลาเต้มนิ้ ท ์': 'ลาเต้มิ้นท์',
    'ลาเต้มนิ้': 'ลาเต้มิ้นท์',
    'มนิ้ ท ์': 'มิ้นท์',
    'มนิ้': 'มิ้นท์',
    'สมิน้': 'มิ้นท์',
    'ไซรปั': 'ไซรัป',
    'นา ้ แขง็': 'น้ำแข็ง',
    'นา ้ แข็ง': 'น้ำแข็ง',
    'นา ้': 'น้ำ',
    'สกดั': 'สกัด',
    'น้ำ สมั': 'น้ำส้ม',
    'น้ำ สม้': 'น้ำส้ม',
    'อุปกรณท์': 'อุปกรณ์',
    'อุปกรณที่': 'อุปกรณ์ที่',
    'ถว้ ยตวง': 'ถ้วยตวง',
    'ถว้ ยชง': 'ถ้วยชง',
    'ถว้ ย': 'ถ้วย',
    'ซอ้ นตกั': 'ช้อนตัก',
    'ซอ้ น': 'ช้อน',
    'เครื่องช่งั': 'เครื่องชั่ง',
    'ช่งั': 'ชั่ง',
    'ดจิ ิตอล': 'ดิจิตอล',
    'กาตม้ นน้ำรอ้ น': 'กาต้มน้ำร้อน',
    'กาตม้': 'กาต้ม',
    'น้ำรอ้ น': 'น้ำร้อน',
    'นาเมล็ด': 'นำเมล็ด',
    'ใหเ้ขา้ กนั': 'ให้เข้ากัน',
    'ถงุ': 'ถุง',
    'เบอร์บั': 'เบอร์บด',
    'เบอรบ์ด': 'เบอร์บด',
    'ใหล้ ะเอียด': 'ให้ละเอียด',
    'ละเฮียด': 'ละเอียด',
    'เพ่อื วอรม์': 'เพื่อวอร์ม',
    'เพ่อื': 'เพื่อ',
    'ตกั': 'ตัก',
    'ปรมาณ': 'ปริมาณ',
    'ขนึ้': 'ขึ้น',
    'ท่เี ขม้': 'ที่เข้ม',
    'ท่ใี ส่': 'ที่ใส่',
    'ท่สี กดั': 'ที่สกัด',
    'ใหท้ ใส่': 'ให้ใส่',
    'แลว้': 'แล้ว',
    'เนยี น': 'เนียน',
    'เสิรฟ์': 'เสิร์ฟ',
    'เสริฟ์': 'เสิร์ฟ',
    'เสริฟ': 'เสิร์ฟ',
    'เสิรฟ': 'เสิร์ฟ',
    'ดว้ ย': 'ด้วย',
    'เตม็': 'เต็ม',
    'สดุ ทา้ ย': 'สุดท้าย',
    'ขนั้ ตอน': 'ขั้นตอน',
    'ขนั้': 'ขั้น',
    'กรมั': 'กรัม',
    'สา หรบั': 'สำหรับ',
    'สำ หรับ': 'สำหรับ',
    'ค่วั': 'คั่ว',
    'เขม้': 'เข้ม',
    'พาสเจอไรซ ์': 'พาสเจอร์ไรซ์',
    'พาสเจอไรซ์': 'พาสเจอร์ไรซ์',
    'ทนั ที': 'ทันที',
    'คาปชู ิโน': 'คาปูชิโน่',
    'คาปูชิโน': 'คาปูชิโน่',
    'มคั คีอาโต้': 'มัคคิอาโต้',
    'มอคคา': 'มอคค่า',
    'มิลลิแปร': 'บาร์',
    'มิลลิแปร์': 'บาร์',
    'แฟลทไวท ์': 'แฟลทไวท์',
    'แฟรบปชู ิโน': 'แฟรบปูชิโน่',
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
    text = re.sub(r'([่้๊๋])\1+', r'\1', text)

    # Normalize Americano missing mai-ek
    text = re.sub(r'อเมริกาโน(?!่)', 'อเมริกาโน่', text)

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
