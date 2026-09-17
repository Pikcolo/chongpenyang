"""
LINE Flex Message Carousel Generator for Barista Drink Recipes.
Renders responsive, elegant coffee cards from the training manual.
"""
from typing import List, Dict, Any

RECIPES_DATA = [
    {
        "name_th": "เอสเพรสโซ่ (Espresso)",
        "name_en": "Single / Double Shot",
        "ratio": "กาแฟ 18-20g / น้ำกาแฟ 30-36g",
        "time": "25 - 30 วินาที",
        "desc": "หัวใจของกาแฟทุกเมนู รสชาติเข้มข้น กลมกล่อม ครีม่าสีทองหนานุ่ม",
        "query": "สูตรและเทคนิคการสกัด Perfect Shot เอสเพรสโซ่",
        "tag": "⭐ เมนูหลัก"
    },
    {
        "name_th": "อเมริกาโน่ (Americano)",
        "name_en": "Hot / Iced Americano",
        "ratio": "Espresso 2 shots + น้ำร้อน/น้ำเย็น 120ml",
        "time": "พร้อมเสิร์ฟทันที",
        "desc": "กาแฟดำรสชาตินุ่มละมุน ดื่มง่าย สกัดรสหวานและกลิ่นหอมเฉพาะตัว",
        "query": "ขอสูตรการทำอเมริกาโน่ร้อนและเย็น",
        "tag": "🔥 ยอดนิยม"
    },
    {
        "name_th": "ลาเต้ (Caffe Latte)",
        "name_en": "Espresso with Steamed Milk",
        "ratio": "Espresso 1-2 shots + นมสตีม 150ml (โฟม 1 ซม.)",
        "time": "อุณหภูมินม 60-65°C",
        "desc": "นมเนียนนุ่มระดับไมโครโฟม ผสานรสชาติกาแฟกลมกล่อม เหมาะทำลาย Latte Art",
        "query": "ขอสูตรการทำลาเต้และเทคนิคการสตีมนม",
        "tag": "🥛 ลาเต้อาร์ต"
    },
    {
        "name_th": "กาแฟส้ม (Black Orange)",
        "name_en": "Orange Juice + Espresso",
        "ratio": "น้ำส้ม 120ml + Espresso 2 shots on top",
        "time": "เสิร์ฟแยกชั้นสวยงาม",
        "desc": "ความสดชื่นหวานอมเปรี้ยวจากน้ำส้มแท้ ตัดกับความเข้มข้นหอมกรุ่นของเอสเพรสโซ่",
        "query": "ขอสูตรกาแฟส้ม (Black Orange Coffee)",
        "tag": "🍊 เมนู Signature"
    },
    {
        "name_th": "เดอร์ตี้ (Dirty Coffee)",
        "name_en": "Cold Milk + Hot Espresso",
        "ratio": "นมเย็นจัด 90ml + Ristretto/Espresso 1 shot on top",
        "time": "แช่นมเย็นจัด 4°C",
        "desc": "สัมผัสมิติอุณหภูมิที่แตกต่าง กาแฟร้อนหอมเข้มไหลตัดผ่านนมเย็นเนื้อสัมผัสเข้มข้น",
        "query": "ขอสูตรและเทคนิคทำกาแฟเดอร์ตี้ (Dirty Coffee)",
        "tag": "✨ เมนูพิเศษ"
    }
]

def create_recipe_bubble(item: Dict[str, Any]) -> Dict[str, Any]:
    """Creates a single Barista Drink Flex Bubble."""
    return {
        "type": "bubble",
        "size": "kilo",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#2C1810",
            "paddingAll": "15px",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": item.get("tag", "☕ กาแฟ"),
                            "size": "xxs",
                            "color": "#D4A373",
                            "weight": "bold"
                        }
                    ]
                },
                {
                    "type": "text",
                    "text": item["name_th"],
                    "weight": "bold",
                    "size": "md",
                    "color": "#FFFFFF",
                    "margin": "sm"
                },
                {
                    "type": "text",
                    "text": item.get("name_en", ""),
                    "size": "xxs",
                    "color": "#E6CCB2"
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "paddingAll": "15px",
            "contents": [
                {
                    "type": "text",
                    "text": item.get("desc", ""),
                    "size": "xs",
                    "color": "#555555",
                    "wrap": True
                },
                {
                    "type": "separator",
                    "margin": "md",
                    "color": "#F0F0F0"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "md",
                    "spacing": "xs",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "อัตราส่วน:", "size": "xxs", "color": "#888888", "flex": 3},
                                {"type": "text", "text": item.get("ratio", ""), "size": "xxs", "color": "#2C1810", "weight": "bold", "flex": 7}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "พารามิเตอร์:", "size": "xxs", "color": "#888888", "flex": 3},
                                {"type": "text", "text": item.get("time", ""), "size": "xxs", "color": "#8B5A2B", "weight": "bold", "flex": 7}
                            ]
                        }
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "paddingAll": "10px",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#8B5A2B",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "📖 ดูวิธีทำตามคู่มือ",
                        "text": item["query"]
                    }
                }
            ]
        }
    }

def create_recipes_carousel_flex() -> Dict[str, Any]:
    """Creates a full Carousel containing all standard Barista recipes."""
    bubbles = [create_recipe_bubble(r) for r in RECIPES_DATA]
    return {
        "type": "carousel",
        "contents": bubbles
    }
