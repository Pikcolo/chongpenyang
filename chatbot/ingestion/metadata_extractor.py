"""
Domain metadata extractor for Barista Training Manual.
Categorizes pages and chunks into precise semantic topics and sections.
"""

import re
from typing import Dict, Any

DOMAIN_TOPICS = [
    {
        "id": "botany_origins",
        "title": "พฤกษศาสตร์ แหล่งกำเนิด และสายพันธุ์กาแฟ",
        "keywords": ["อาราบิก้า", "โรบัสต้า", "สายพันธุ์", "แหล่งกำเนิด", "กาแฟคือ", "ความแตกต่าง", "arabica", "robusta"]
    },
    {
        "id": "tree_to_cup",
        "title": "10 ขั้นตอนจากต้นสู่แก้ว (From Tree to Cup)",
        "keywords": ["ต้นสู่แก้ว", "เก็บเกี่ยว", "แปรรูป", "สารกาแฟ", "process", "wet process", "dry process", "honey"]
    },
    {
        "id": "roasting",
        "title": "วิทยาศาสตร์การคั่วกาแฟและระดับการคั่ว (Roasting & Agtron)",
        "keywords": ["การคั่ว", "ระดับการคั่ว", "agtron", "light roast", "medium roast", "dark roast", "คั่วอ่อน", "คั่วกลาง", "คั่วเข้ม", "first crack", "second crack"]
    },
    {
        "id": "grinding_espresso",
        "title": "การปรับเบอร์บดและการสกัดเอสเพรสโซ่ (Grind Size & Extraction)",
        "keywords": ["เบอร์บด", "การบด", "การสกัด", "dosing", "tamping", "แทมป์", "ช็อต", "espresso", "crema", "อัตราส่วนการสกัด", "อุณหภูมิ", "แรงดัน"]
    },
    {
        "id": "troubleshooting",
        "title": "การวิเคราะห์และแก้ไขปัญหาการสกัด (Under / Over Extraction)",
        "keywords": ["under-extraction", "over-extraction", "สกัดน้อยเกินไป", "สกัดมากเกินไป", "เปรี้ยวฝาด", "ขมไหม้", "channeling", "ไหลเร็ว", "ไหลช้า", "ฟองครีม่า"]
    },
    {
        "id": "milk_steaming",
        "title": "การสตีมนม โฟมนม และศิลปะลาเต้อาร์ต (Milk Steaming & Latte Art)",
        "keywords": ["สตีมนม", "โฟมนม", "ก้านสตรีม", "เหยือกสตีม", "พิชเชอร์", "latte art", "ไมโครโฟม", "อุณหภูมินม", "สตรีมนม"]
    },
    {
        "id": "recipes_hot",
        "title": "สูตรมาตรฐานเครื่องดื่มร้อน (Hot Coffee Recipes)",
        "keywords": ["สูตรกาแฟร้อน", "hot espresso", "hot americano", "hot latte", "hot cappuccino", "hot mocha", "เอสเพรสโซ่ร้อน", "อเมริกาโน่ร้อน", "ลาเต้ร้อน", "คาปูชิโน่ร้อน", "มอคค่าร้อน"]
    },
    {
        "id": "recipes_cold",
        "title": "สูตรมาตรฐานเครื่องดื่มเย็น (Iced Coffee Recipes)",
        "keywords": ["สูตรกาแฟเย็น", "iced americano", "iced latte", "iced cappuccino", "iced mocha", "เอสเพรสโซ่เย็น", "อเมริกาโน่เย็น", "ลาเต้เย็น", "คาปูชิโน่เย็น", "มอคค่าเย็น", "กาแฟส้ม", "dirty"]
    },
    {
        "id": "maintenance_sop",
        "title": "การบำรุงรักษาเครื่องชงและขั้นตอนปฏิบัติงานมาตรฐาน (Maintenance & SOP)",
        "keywords": ["ทำความสะอาด", "ล้างเครื่อง", "backflush", "บำรุงรักษา", "ความปลอดภัย", "sop", "สุขอนามัย"]
    }
]

def detect_topic(text: str, default_title: str = "คู่มือประกอบการฝึกอบรม หลักสูตร: บาริสต้ามืออาชีพ") -> Dict[str, str]:
    """Detects the primary topic and category from the text content."""
    text_lower = text.lower()
    best_topic = None
    max_matches = 0

    for topic in DOMAIN_TOPICS:
        matches = sum(1 for kw in topic["keywords"] if kw.lower() in text_lower)
        if matches > max_matches:
            max_matches = matches
            best_topic = topic

    if best_topic and max_matches > 0:
        return {
            "topic_id": best_topic["id"],
            "topic_title": best_topic["title"],
            "document_name": default_title
        }

    return {
        "topic_id": "general_barista",
        "topic_title": "ความรู้ทั่วไปและมาตรฐานบาริสต้า",
        "document_name": default_title
    }
