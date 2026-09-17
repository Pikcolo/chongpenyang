"""
Contextual Quick Reply generator for Chongpenyang Barista Assistant.
Provides quick-action chips for fast, seamless user interaction on LINE and Web.
"""
from typing import List, Dict, Any

BARISTA_QUICK_REPLY_ITEMS = [
    {
        "label": "☕ Perfect Shot",
        "text": "สูตรและเทคนิคการสกัด Perfect Shot เอสเพรสโซ่"
    },
    {
        "label": "🥛 เทคนิคสตีมนม",
        "text": "เทคนิคการสตีมนมและทำลาเต้อาร์ต อุณหภูมิเท่าไร?"
    },
    {
        "label": "⚙️ ปรับเบอร์บด",
        "text": "วิธีปรับเบอร์บดเครื่องบดกาแฟให้เหมาะสม"
    },
    {
        "label": "🍊 สูตรกาแฟส้ม",
        "text": "ขอสูตรกาแฟส้ม (Black Orange Coffee)"
    },
    {
        "label": "🔬 แก้รสเปรี้ยว/ขม",
        "text": "วิธีแก้ปัญหากาแฟรสชาติเปรี้ยวเกินไปหรือขมเกินไป"
    },
    {
        "label": "📖 สารบัญคู่มือ",
        "text": "สารบัญหัวข้อทั้งหมดในคู่มือบาริสต้ามืออาชีพ"
    }
]

def get_barista_quick_replies() -> Dict[str, Any]:
    """
    Returns standard LINE v3 QuickReply JSON payload with 6 focused barista chips.
    """
    items = []
    for item in BARISTA_QUICK_REPLY_ITEMS:
        items.append({
            "type": "action",
            "action": {
                "type": "message",
                "label": item["label"],
                "text": item["text"]
            }
        })
    return {"items": items}

def get_quick_reply_list() -> List[Dict[str, str]]:
    """Returns a simple list of chips for Web UI simulator."""
    return BARISTA_QUICK_REPLY_ITEMS
