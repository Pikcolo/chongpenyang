"""
Contextual Quick Reply generator for Chongpenyang Barista Assistant.
Organized strictly according to the 5 Official Curriculum Modules:
- MOD_01: Coffee Botany, Species, Roasting (Agtron 80-70 to 30-25), Tree-to-Cup, 5 Grind Sizes
- MOD_02: Extraction Science (90-96°C, 9-10 Bar), Under/Over Extraction, Channeling & WDT, Maintenance
- MOD_03: Latte Art History (David Schomer, WLAC 2019), Milk Chemistry (Microfoam 60-65°C), Free Pour
- MOD_04: 13 Standard SOP Recipes (Hot/Iced Drinks, Orange, Peach, Mint Latte, Honey Lemon, etc.)
- MOD_05: Barista Tests, Skill Checklists, and Standard Answer Keys
All labels are strictly <= 20 characters per LINE Messaging API requirements.
"""

from typing import List, Dict, Any

# ==============================================================================
# 5 Module Quick Reply Pools (All labels strictly <= 20 chars)
# ==============================================================================

MOD_01_BEANS_ROAST_QUICK_REPLIES = [
    {"label": "🎨 สเกล Agtron", "text": "ระดับการคั่วกาแฟและสเกล Agtron มีอะไรบ้าง"},
    {"label": "🍒 อาราบิก้า vs โรบัสต้า", "text": "เมล็ดกาแฟอาราบิก้า กับ โรบัสต้า ต่างกันอย่างไร"},
    {"label": "🌍 กาแฟจากต้นสู่แก้ว", "text": "ขั้นตอนการผลิตกาแฟจากต้นสู่แก้วมีอะไรบ้าง"},
    {"label": "⚙️ เบอร์บด 5 ระดับ", "text": "เบอร์บดกาแฟ 5 ระดับและการเลือกใช้อุปกรณ์"},
    {"label": "🐐 ตำนานกาแฟ Kaldi", "text": "ประวัติการค้นพบกาแฟและตำนาน Kaldi คืออะไร"},
    {"label": "☕ การ Cupping ชิมกาแฟ", "text": "การทดสอบชิมกาแฟ Cupping มีขั้นตอนอย่างไร"},
    {"label": "💥 First vs Second Crack", "text": "First Crack กับ Second Crack ในการคั่วกาแฟต่างกันอย่างไร"},
    {"label": "📖 สารบัญ 5 โมดูล", "text": "ขอสารบัญ 5 โมดูลหลักสูตรบาริสต้า"}
]

MOD_02_EXTRACTION_QUICK_REPLIES = [
    {"label": "☕ สกัด Perfect Shot", "text": "พารามิเตอร์การสกัด Perfect Shot เอสเพรสโซ่คืออะไร"},
    {"label": "🛡️ แก้ Channeling", "text": "Channeling คืออะไรและมีวิธีป้องกันอย่างไร"},
    {"label": "⚠️ กาแฟสกัดขาด Under", "text": "สาเหตุและวิธีแก้ปัญหากาแฟสกัดขาด Under-Extraction"},
    {"label": "⚠️ กาแฟสกัดเกิน Over", "text": "สาเหตุและวิธีแก้ปัญหากาแฟสกัดเกิน Over-Extraction"},
    {"label": "🌡️ อุณหภูมิและแรงดัน", "text": "อุณหภูมิน้ำและแรงดันในการสกัดเอสเพรสโซ่ที่เหมาะสม"},
    {"label": "🔍 ด้ามชง Bottomless", "text": "ด้ามชงแบบ Bottomless มีประโยชน์อย่างไร"},
    {"label": "🧼 ล้างเครื่อง Backflush", "text": "ขั้นตอนการทำ Backflush เครื่องชงกาแฟ"},
    {"label": "📖 สารบัญ 5 โมดูล", "text": "ขอสารบัญ 5 โมดูลหลักสูตรบาริสต้า"}
]

MOD_03_LATTE_ART_QUICK_REPLIES = [
    {"label": "🥛 ฟองนม Microfoam", "text": "วิทยาศาสตร์การสตีมนมและอุณหภูมิฟองนมที่เหมาะสม"},
    {"label": "🏛️ กำเนิด Latte Art", "text": "ประวัติและต้นกำเนิด Latte Art"},
    {"label": "🏆 แชมป์ WLAC 2019", "text": "แชมป์ World Latte Art 2019 คือใครและใช้ลายอะไร"},
    {"label": "🌿 ลายแรก Rosetta", "text": "ประวัติความเป็นมาของลาย Rosetta"},
    {"label": "🎨 Free Pour vs Etching", "text": "เทคนิคการเท Free Pour กับ Etching ต่างกันอย่างไร"},
    {"label": "⚙️ หัวฉีดไอน้ำ 1901", "text": "ใครเป็นผู้คิดค้นหัวฉีดไอน้ำสตีมนมคนแรก"},
    {"label": "📖 สารบัญ 5 โมดูล", "text": "ขอสารบัญ 5 โมดูลหลักสูตรบาริสต้า"}
]

MOD_04_RECIPES_QUICK_REPLIES = [
    {"label": "🍊 สูตรกาแฟส้ม", "text": "ขอสูตรและวิธีทำกาแฟส้ม Black Orange Coffee"},
    {"label": "🍑 สูตรกาแฟพีช", "text": "ขอสูตรและวิธีทำกาแฟพีช"},
    {"label": "🍋 กาแฟน้ำผึ้งมะนาว", "text": "ขอสูตรและวิธีทำกาแฟน้ำผึ้งมะนาว"},
    {"label": "🍃 สูตรลาเต้มิ้นท์", "text": "ขอสูตรและวิธีทำลาเต้มิ้นท์"},
    {"label": "🧊 เอสเพรสโซ่เย็น", "text": "ขอสูตรและวิธีทำเอสเพรสโซ่เย็นสไตล์ไทย"},
    {"label": "☕ อเมริกาโน่ร้อน", "text": "ขอสูตรและวิธีทำอเมริกาโน่ร้อน Hot Americano"},
    {"label": "🧊 อเมริกาโน่เย็น", "text": "ขอสูตรและวิธีทำอเมริกาโน่เย็น Iced Americano"},
    {"label": "☕ ลาเต้ vs คาปูชิโน่", "text": "ลาเต้ร้อน กับ คาปูชิโน่ร้อน ต่างกันอย่างไร"},
    {"label": "📖 สารบัญ 5 โมดูล", "text": "ขอสารบัญ 5 โมดูลหลักสูตรบาริสต้า"}
]

MOD_05_EVAL_TEST_QUICK_REPLIES = [
    {"label": "📝 แบบทดสอบบาริสต้า", "text": "แบบทดสอบวัดความรู้บาริสต้ามีอะไรบ้าง"},
    {"label": "📋 เช็กลิสต์ทักษะบาร์", "text": "Checklist ตรวจสอบทักษะการทำงานในบาร์กาแฟ"},
    {"label": "☕ เกณฑ์ Perfect Shot", "text": "เกณฑ์มาตรฐานและเฉลยการสกัด Perfect Shot"},
    {"label": "📖 สารบัญ 5 โมดูล", "text": "ขอสารบัญ 5 โมดูลหลักสูตรบาริสต้า"}
]

DEFAULT_BARISTA_QUICK_REPLIES = [
    {"label": "☕ สกัด Perfect Shot", "text": "พารามิเตอร์การสกัด Perfect Shot เอสเพรสโซ่คืออะไร"},
    {"label": "🛡️ แก้ Channeling", "text": "Channeling คืออะไรและมีวิธีป้องกันอย่างไร"},
    {"label": "⚠️ กาแฟสกัดเกิน Over", "text": "สาเหตุและวิธีแก้ปัญหากาแฟสกัดเกิน Over-Extraction"},
    {"label": "🍊 สูตรกาแฟส้ม", "text": "ขอสูตรและวิธีทำกาแฟส้ม Black Orange Coffee"},
    {"label": "🍑 สูตรกาแฟพีช", "text": "ขอสูตรและวิธีทำกาแฟพีช"},
    {"label": "🍃 สูตรลาเต้มิ้นท์", "text": "ขอสูตรและวิธีทำลาเต้มิ้นท์"},
    {"label": "🥛 ฟองนม Microfoam", "text": "วิทยาศาสตร์การสตีมนมและอุณหภูมิฟองนมที่เหมาะสม"},
    {"label": "🎨 สเกล Agtron", "text": "ระดับการคั่วกาแฟและสเกล Agtron มีอะไรบ้าง"},
    {"label": "🍒 อาราบิก้า vs โรบัสต้า", "text": "เมล็ดกาแฟอาราบิก้า กับ โรบัสต้า ต่างกันอย่างไร"},
    {"label": "☕ ลาเต้ vs คาปูชิโน่", "text": "ลาเต้ร้อน กับ คาปูชิโน่ร้อน ต่างกันอย่างไร"},
    {"label": "📖 สารบัญ 5 โมดูล", "text": "ขอสารบัญ 5 โมดูลหลักสูตรบาริสต้า"}
]


# ==============================================================================
# Contextual Dispatcher
# ==============================================================================

def select_contextual_chips(user_query: str = "", reply_text: str = "") -> List[Dict[str, str]]:
    """
    Selects relevant quick reply buttons dynamically based on ongoing conversation context.
    Maps to the 5 official curriculum modules.
    """
    context = (user_query + " " + reply_text).lower()

    # Module 04: Recipes & Drink SOP
    if any(k in context for k in ["สูตร", "เมนู", "ส้ม", "พีช", "มะนาว", "มิ้นท์", "เย็น", "ร้อน", "americano", "latte", "cappuccino", "sop", "ส่วนผสม"]):
        return MOD_04_RECIPES_QUICK_REPLIES

    # Module 03: Milk Chemistry & Latte Art
    if any(k in context for k in ["นม", "สตีม", "สตรีม", "โฟม", "microfoam", "ลาเต้อาร์ต", "latte art", "rosetta", "david", "schomer", "bezzera", "wlac", "เคซีน"]):
        return MOD_03_LATTE_ART_QUICK_REPLIES

    # Module 02: Extraction Science & Troubleshooting
    if any(k in context for k in ["สกัด", "extract", "channel", "perfect shot", "under", "over", "เปรี้ยว", "ขม", "ไหม้", "บาร์", "แรงดัน", "ครีม่า", "crema", "backflush", "bottomless", "แทมป์"]):
        return MOD_02_EXTRACTION_QUICK_REPLIES

    # Module 01: Botany, Green Beans, Roasting, Grinding
    if any(k in context for k in ["เมล็ด", "สายพันธุ์", "อาราบิก้า", "arabica", "โรบัสต้า", "robusta", "peaberry", "คั่ว", "roast", "agtron", "cupping", "tree to cup", "แปรรูป", "บด", "crack"]):
        return MOD_01_BEANS_ROAST_QUICK_REPLIES

    # Module 05: Evaluation, Worksheets, Checklist
    if any(k in context for k in ["แบบทดสอบ", "ใบทดสอบ", "ใบงาน", "checklist", "เช็กลิสต์", "เฉลย", "ประเมิน"]):
        return MOD_05_EVAL_TEST_QUICK_REPLIES

    return DEFAULT_BARISTA_QUICK_REPLIES


def get_barista_quick_replies(user_query: str = "", reply_text: str = "") -> Dict[str, Any]:
    """
    Returns standard LINE QuickReply JSON payload with context-aware buttons.
    Guarantees every label is strictly <= 20 characters for LINE API compliance.
    """
    chips = select_contextual_chips(user_query, reply_text)
    items = []
    for item in chips[:12]:
        lbl = item["label"].strip()
        if len(lbl) > 20:
            lbl = lbl[:20]
        items.append({
            "type": "action",
            "action": {
                "type": "message",
                "label": lbl,
                "text": item["text"]
            }
        })
    return {"items": items}


def get_line_sdk_quick_reply(user_query: str = "", reply_text: str = ""):
    """
    Constructs a LINE Python SDK QuickReply object directly ready for TextSendMessage or FlexSendMessage.
    """
    try:
        from linebot.models import QuickReply, QuickReplyButton, MessageAction
        chips = select_contextual_chips(user_query, reply_text)
        buttons = []
        for item in chips[:12]:
            lbl = item["label"].strip()[:20]
            buttons.append(
                QuickReplyButton(
                    action=MessageAction(label=lbl, text=item["text"])
                )
            )
        return QuickReply(items=buttons) if buttons else None
    except Exception as e:
        return None


def get_quick_reply_list(user_query: str = "", reply_text: str = "") -> List[Dict[str, str]]:
    """Returns a list of chips for Web UI simulator."""
    return select_contextual_chips(user_query, reply_text)
