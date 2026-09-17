"""
Domain metadata extractor for Barista Training Manual.
Categorizes pages and chunks into the official 5 modules (MOD_01 to MOD_05)
based on explicit page ranges and curriculum topics from documents.pdf.
"""

import re
from typing import Dict, Any, Optional

# Official 5 Modules defined by the Barista Training Curriculum
OFFICIAL_MODULES = [
    {
        "id": "MOD_01",
        "title": "โมดูลที่ 1: ความรู้เบื้องต้นเกี่ยวกับเมล็ดกาแฟ",
        "short_title": "ความรู้เบื้องต้นเกี่ยวกับเมล็ดกาแฟ",
        "page_start": 3,
        "page_end": 19,
        "scope": [
            "ประวัติความเป็นมาและแหล่งกำเนิดกาแฟโลก",
            "สายพันธุ์กาแฟหลัก (Arabica, Robusta, Peaberry)",
            "สายพันธุ์ย่อยยอดนิยม (Typica, Bourbon, Caturra, Catuai, Geisha, ฯลฯ)",
            "ปัจจัยการเพาะปลูก (ระดับความสูง, อุณหภูมิ, ปริมาณน้ำฝน)",
            "10 ขั้นตอนการผลิตจากต้นสู่แก้ว (ปลูก, เก็บเกี่ยว, แปรรูป, สีเมล็ด, คัดเกรด, Cupping, คั่ว, บด, ชง)",
            "ระดับการคั่ว (Light, Medium, Dark/French Roast) และสเกล Agtron",
            "เบอร์บดกาแฟ 5 ระดับ (Extra Fine ถึง Coarse) และการเลือกใช้อุปกรณ์ชง"
        ],
        "keywords": [
            "อาราบิก้า", "โรบัสต้า", "สายพันธุ์", "แหล่งกำเนิด", "arabica", "robusta", "peaberry",
            "typica", "bourbon", "geisha", "catuai", "caturra", "ต้นสู่แก้ว", "เก็บเกี่ยว", "แปรรูป",
            "washed", "dry process", "wet process", "honey process", "cupping", "การคั่ว", "agtron",
            "ระดับการคั่ว", "คั่วอ่อน", "คั่วกลาง", "คั่วเข้ม", "เบอร์บด", "ความละเอียดบด", "grinder"
        ]
    },
    {
        "id": "MOD_02",
        "title": "โมดูลที่ 2: เคล็ดลับการชงกาแฟ หลักการและวิธีการ",
        "short_title": "เคล็ดลับการชงกาแฟ หลักการและวิธีการ",
        "page_start": 20,
        "page_end": 31,
        "scope": [
            "วิทยาศาสตร์การสกัดกาแฟ (Extraction Parameters)",
            "คุณภาพน้ำ, อุณหภูมิน้ำในการสกัด (88–95°C), แรงดัน (9-10 บาร์)",
            "การประเมินสถานะการสกัด: Espresso Perfect, Under Extraction, Over Extraction",
            "อาการของครีมม่า (Crema), รสชาติ (Sensory Profile), สาเหตุ และแนวทางแก้ไข",
            "Channeling และการปรับตั้งเครื่องบด/แรงแทมป์"
        ],
        "keywords": [
            "การสกัด", "สกัด", "extraction", "espresso perfect", "perfect shot", "under extraction",
            "over extraction", "สกัดน้อยเกินไป", "สกัดมากเกินไป", "เปรี้ยวฝาด", "ขมไหม้", "crema",
            "ครีม่า", "ครีมม่า", "channeling", "แรงดัน", "บาร์", "อุณหภูมิน้ำ", "dosing", "tamping",
            "แทมป์", "ไหลเร็ว", "ไหลช้า", "เซนเซอร์รี่", "sensory"
        ]
    },
    {
        "id": "MOD_03",
        "title": "โมดูลที่ 3: ประวัติความเป็นมาและศาสตร์ของลาเต้อาร์ต",
        "short_title": "ประวัติความเป็นมาและศาสตร์ของลาเต้อาร์ต",
        "page_start": 32,
        "page_end": 36,
        "scope": [
            "ประวัติและต้นกำเนิด Latte Art (David Schomer / Espresso Vivace, Seattle)",
            "การแข่งขัน World Latte Art Championship (WLAC)",
            "วิทยาศาสตร์ฟองนม (Microfoam): โปรตีนเคซีนและไขมันนมที่อุณหภูมิ 60–65°C",
            "เทคนิคการเท 2 รูปแบบ: Free Pour (ลาย Heart, Tulip, Rosetta) และ Etching (การวาดลาย)"
        ],
        "keywords": [
            "ลาเต้อาร์ต", "latte art", "สตีมนม", "โฟมนม", "microfoam", "ไมโครโฟม", "ฟองนม",
            "david schomer", "wlac", "world latte art", "เคซีน", "casein", "โปรตีนนม",
            "free pour", "etching", "rosetta", "tulip", "heart", "หัวฉีดไอน้ำ", "pitcher", "พิชเชอร์"
        ]
    },
    {
        "id": "MOD_04",
        "title": "โมดูลที่ 4: ใบขั้นตอนการปฏิบัติงาน การชงกาแฟร้อนและเย็น (SOP)",
        "short_title": "ใบขั้นตอนการปฏิบัติงาน การชงกาแฟร้อนและเย็น (SOP)",
        "page_start": 37,
        "page_end": 50,
        "scope": [
            "สูตรและสัดส่วนมาตรฐานของเมนูกาแฟ 13 เมนู (ร้อน 5 เมนู, เย็น 8 เมนู)",
            "อัตราส่วนวัตถุดิบ (Dose, Yield, สัดส่วนนม/น้ำเชื่อม/น้ำผลไม้)",
            "อุปกรณ์เฉพาะทางและเครื่องบด/เครื่องชงประจำเมนู",
            "ขั้นตอน Standard Operating Procedure (SOP) ทีละสเต็ป",
            "เทคนิคและ Barista Tips ประจำแต่ละเมนู"
        ],
        "keywords": [
            "sop", "สูตร", "วิธีทำ", "ขั้นตอนการปฏิบัติงาน", "ส่วนผสม", "วัตถุดิบ", "americano",
            "latte", "cappuccino", "mocha", "espresso", "อเมริกาโน่", "ลาเต้", "คาปูชิโน่", "มอคค่า",
            "กาแฟส้ม", "กาแฟพีช", "ลาเต้มิ้นท์", "น้ำผึ้งมะนาว", "lemonade", "dirty", "กาแฟร้อน", "กาแฟเย็น"
        ]
    },
    {
        "id": "MOD_05",
        "title": "โมดูลที่ 5: ใบงาน ใบทดสอบ และใบเฉลย",
        "short_title": "ใบงาน ใบทดสอบ และใบเฉลย",
        "page_start": 51,
        "page_end": 53,
        "scope": [
            "แบบทดสอบวัดระดับความรู้บาริสต้า",
            "Checklist ตรวจสอบทักษะการชงและการจัดการบาร์",
            "แนวทางปฏิบัติและเฉลยคำตอบมาตรฐาน"
        ],
        "keywords": [
            "ใบงาน", "ใบทดสอบ", "ใบเฉลย", "แบบทดสอบ", "checklist", "เกณฑ์การประเมิน",
            "แบบประเมิน", "เฉลย", "แบบฝึกหัด", "ข้อสอบ", "คะแนน"
        ]
    }
]

INTRO_MODULE = {
    "id": "MOD_00",
    "title": "บทนำและสารบัญหลักสูตร",
    "short_title": "บทนำและสารบัญคู่มือบาริสต้ามืออาชีพ",
    "page_start": 1,
    "page_end": 2
}

def get_module_by_page(page_no: int) -> Dict[str, Any]:
    """Returns official module info strictly based on document page number."""
    if 1 <= page_no <= 2:
        return INTRO_MODULE
    for mod in OFFICIAL_MODULES:
        if mod["page_start"] <= page_no <= mod["page_end"]:
            return mod
    # Fallback to closest module
    if page_no > 53:
        return OFFICIAL_MODULES[-1]
    return OFFICIAL_MODULES[0]

def detect_topic(
    text: str,
    page_no: Optional[int] = None,
    default_title: str = "คู่มือประกอบการฝึกอบรม หลักสูตร: บาริสต้ามืออาชีพ"
) -> Dict[str, str]:
    """
    Detects the official module (MOD_01 to MOD_05) and descriptive topic title.
    Prioritizes exact page number when available, combined with semantic context.
    """
    # 1. If page number is explicitly provided, map to official module
    if page_no is not None and page_no > 0:
        mod = get_module_by_page(page_no)
        # Check for sub-topic detail within text
        subtopic = _extract_subtopic(text, mod)
        full_title = f"{mod['title']} ({subtopic})" if subtopic else mod['title']
        return {
            "topic_id": mod["id"].lower(),
            "module_id": mod["id"],
            "topic_title": full_title,
            "module_name": mod["short_title"],
            "document_name": default_title
        }

    # 2. Extract page pattern from text if present: e.g. [หน้า 24] or หน้า 24
    match = re.search(r'\[?\s*หน้า\s*(\d+)', text)
    if match:
        extracted_page = int(match.group(1))
        return detect_topic(text, page_no=extracted_page, default_title=default_title)

    # 3. Fallback to keyword matching across official modules
    text_lower = text.lower()
    best_mod = OFFICIAL_MODULES[0]
    max_score = -1

    for mod in OFFICIAL_MODULES:
        score = sum(1 for kw in mod["keywords"] if kw in text_lower)
        if score > max_score:
            max_score = score
            best_mod = mod

    subtopic = _extract_subtopic(text, best_mod)
    full_title = f"{best_mod['title']} ({subtopic})" if subtopic else best_mod['title']

    return {
        "topic_id": best_mod["id"].lower(),
        "module_id": best_mod["id"],
        "topic_title": full_title,
        "module_name": best_mod["short_title"],
        "document_name": default_title
    }

def _extract_subtopic(text: str, mod: Dict[str, Any]) -> Optional[str]:
    """Extracts granular subtopic within a module for richer citation."""
    t = text.lower()
    if mod["id"] == "MOD_01":
        if any(k in t for k in ["agtron", "การคั่ว", "ระดับการคั่ว", "roast"]):
            return "การคั่วกาแฟและสเกล Agtron"
        if any(k in t for k in ["เบอร์บด", "ความละเอียด", "grind"]):
            return "เบอร์บด 5 ระดับและการเลือกอุปกรณ์"
        if any(k in t for k in ["ต้นสู่แก้ว", "แปรรูป", "process", "เก็บเกี่ยว"]):
            return "10 ขั้นตอนจากต้นสู่แก้ว"
        if any(k in t for k in ["arabica", "robusta", "peaberry", "สายพันธุ์"]):
            return "พฤกษศาสตร์และสายพันธุ์กาแฟ"
    elif mod["id"] == "MOD_02":
        if any(k in t for k in ["under", "over", "เปรี้ยว", "ขม", "สกัดน้อย", "สกัดมาก"]):
            return "การวิเคราะห์ปัญหา Under/Over Extraction"
        if any(k in t for k in ["channeling", "แทมป์", "tamp", "บาสเก็ต"]):
            return "Channeling และเทคนิคการแทมป์"
        if any(k in t for k in ["perfect shot", "เอสเพรสโซ่", "อุณหภูมิ", "แรงดัน", "บาร์"]):
            return "วิทยาศาสตร์การสกัด Perfect Shot"
    elif mod["id"] == "MOD_03":
        if any(k in t for k in ["microfoam", "ฟองนม", "เคซีน", "อุณหภูมินม", "60-65"]):
            return "วิทยาศาสตร์ฟองนม Microfoam 60-65°C"
        if any(k in t for k in ["david schomer", "ประวัติ", "wlac", "ต้นกำเนิด"]):
            return "ประวัติศาสตร์และต้นกำเนิด Latte Art"
        if any(k in t for k in ["free pour", "etching", "rosetta", "tulip", "heart"]):
            return "เทคนิคการเท Free Pour & Etching"
    elif mod["id"] == "MOD_04":
        if any(k in t for k in ["สูตร", "วิธีทำ", "ส่วนผสม", "sop", "อเมริกาโน่", "ลาเต้", "กาแฟส้ม"]):
            return "สูตรเครื่องดื่มมาตรฐานและขั้นตอน SOP"
    elif mod["id"] == "MOD_05":
        return "แบบทดสอบและ Checklist มาตรฐาน"
    return None

