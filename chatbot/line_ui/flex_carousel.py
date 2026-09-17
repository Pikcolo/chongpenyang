"""
LINE Flex Message Carousel Generator for Barista Drink Recipes.
Renders responsive, elegant coffee cards synthesized directly from the training manual:
คู่มือประกอบการฝึกอบรม หลักสูตร: บาริสต้ามืออาชีพ (MOD_02, MOD_03, MOD_04).
"""
from typing import List, Dict, Any

# 8 Standard & Specialty Beverages directly present with SOP pages in documents.pdf (Pages 39-50)
RECIPES_DATA: List[Dict[str, Any]] = [
    {
        "id": "espresso",
        "name_th": "เอสเพรสโซ่ (หน้า 39)",
        "name_en": "Hot Espresso Shot",
        "tag": "⭐ เมนูมาตรฐาน (หน้า 39)",
        "badge_color": "#FFD54F",
        "header_bg": "#1F130B",
        "desc": "กาแฟช็อตเข้มข้น สกัดจากเมล็ดกาแฟคั่วบดละเอียด เป็นฐานสำคัญของเครื่องดื่มกาแฟทุกชนิด",
        "ratio": "กาแฟบดละเอียด 1 ช็อต / เสิร์ฟในแก้วช็อต",
        "params": "สกัดผ่านเครื่องชงเอสเพรสโซ่ | เสิร์ฟร้อนทันที",
        "standard": "ครีม่าสีทองหนานุ่ม รสชาติเข้มข้น หอมกรุ่น",
        "tip": "อุ่นแก้วกาแฟก่อนสกัดเสมอ และเสิร์ฟทันทีขณะครีม่ายังลอยตัว",
        "query_sop": "สูตรและขั้นตอนการทำเอสเพรสโซ่ตามคู่มือ (หน้า 39)",
        "query_param": "การสกัดกาแฟที่สมบูรณ์แบบ (Ideal-extracted) ในคู่มือมีลักษณะอย่างไร?"
    },
    {
        "id": "hot_americano",
        "name_th": "อเมริกาโน่ร้อน (หน้า 40)",
        "name_en": "Hot Americano",
        "tag": "☕ กาแฟร้อน (หน้า 40)",
        "badge_color": "#FFCC80",
        "header_bg": "#281812",
        "desc": "การผสมผสานกาแฟเอสเพรสโซ่ 1-2 ช็อต กับน้ำร้อน เพื่อให้ได้กาแฟดำที่ดื่มง่าย นุ่มละมุน",
        "ratio": "Espresso 1-2 ช็อต ผสมกับน้ำร้อน",
        "params": "เสิร์ฟในแก้วร้อนขนาดมาตรฐาน | อุณหภูมิน้ำร้อนพอเหมาะ",
        "standard": "กาแฟดำรสชาตินุ่ม ไม่ขมไหม้ คงกลิ่นหอมอโรมา",
        "tip": "ใช้น้ำร้อนสะอาดในการผสมเพื่อไม่ให้กลิ่นแปลกปลอมรบกวนรสกาแฟ",
        "query_sop": "สูตรและขั้นตอนการทำอเมริกาโน่ร้อนตามคู่มือ (หน้า 40)",
        "query_param": "ขั้นตอนการทำอเมริกาโน่ร้อนในคู่มือหน้า 40 มีอะไรบ้าง?"
    },
    {
        "id": "iced_americano",
        "name_th": "อเมริกาโน่เย็น (หน้า 45)",
        "name_en": "Iced Americano",
        "tag": "🧊 ยอดนิยม (หน้า 45)",
        "badge_color": "#64B5F6",
        "header_bg": "#141E28",
        "desc": "กาแฟดำเย็นสดชื่น สกัดจากเมล็ดกาแฟดอยไทยคั่วกลาง (ถุงแดง) บดละเอียดผสมน้ำเย็นและน้ำแข็ง",
        "ratio": "กาแฟดอยไทยคั่วกลาง 15g + น้ำเย็น + น้ำแข็ง",
        "params": "บดละเอียดกว่าน้ำตาลทราย | เสิร์ฟเย็นในแก้ว",
        "standard": "รสชาติเข้มข้นพอดี สดชื่น สะอาด ดับกระหาย",
        "tip": "ใส่น้ำเย็นและน้ำแข็งก่อน แล้วเทกาแฟเอสเพรสโซ่ด้านบน",
        "query_sop": "สูตรและวิธีทำอเมริกาโน่เย็นตามคู่มือ (หน้า 45)",
        "query_param": "อุปกรณ์และวัตถุดิบที่ใช้ทำอเมริกาโน่เย็นหน้า 45 มีอะไรบ้าง?"
    },
    {
        "id": "iced_espresso",
        "name_th": "เอสเพรสโซ่เย็น (หน้า 47)",
        "name_en": "Iced Espresso",
        "tag": "🔥 เมนูยอดนิยม (หน้า 47)",
        "badge_color": "#FFB74D",
        "header_bg": "#2B1608",
        "desc": "กาแฟเย็นสไตล์เข้มข้น ใช้กาแฟดอยไทยคั่วเข้มมาก (French Roast) ผสมนมข้นหวานและนมสด หวานมันกลมกล่อม",
        "ratio": "กาแฟคั่วเข้ม 15g + นมข้นหวาน + นมสด",
        "params": "บดละเอียด | แก้วเสิร์ฟเย็นพร้อมน้ำแข็ง",
        "standard": "รสชาติเข้มข้น หวานมัน กลมกล่อม ไม่จืดชืด",
        "tip": "ละลายนมข้นหวานกับกาแฟร้อนให้เข้ากันดีก่อนเทลงน้ำแข็ง",
        "query_sop": "สูตร ส่วนผสม และวิธีทำเอสเพรสโซ่เย็นตามคู่มือ (หน้า 47)",
        "query_param": "ส่วนผสมเอสเพรสโซ่เย็นในคู่มือหน้า 47 มีอะไรบ้าง?"
    },
    {
        "id": "black_orange",
        "name_th": "กาแฟส้ม (หน้า 50)",
        "name_en": "Black Orange Coffee",
        "tag": "🍊 ผลไม้สดชื่น (หน้า 50)",
        "badge_color": "#FFA726",
        "header_bg": "#2E1502",
        "desc": "เมนูกาแฟส้มยอดนิยม ใช้น้ำส้มสายน้ำผึ้ง ผสมโซดา และเมล็ดกาแฟดอยไทยคั่วกลาง ให้รสเปรี้ยวหวานซ่าสดชื่น",
        "ratio": "น้ำส้มสายน้ำผึ้ง 2 ออนซ์ + โซดา 3 ออนซ์ + กาแฟคั่วกลาง 1 ช็อต",
        "params": "น้ำแข็งแน่นแก้ว | เทกาแฟแยกชั้นทูโทนสวยงาม",
        "standard": "สีสันแยก 2 ชั้น รสชาติหวานอมเปรี้ยวซ่าตัดความเข้มกาแฟ",
        "tip": "ค่อยๆ เทกาแฟด้านบนผ่านน้ำแข็งเพื่อรักษาการแยกชั้นให้สวยงาม",
        "query_sop": "สูตร ส่วนผสม และวิธีทำกาแฟส้มตามคู่มือ (หน้า 50)",
        "query_param": "ส่วนผสมกาแฟส้มในคู่มือหน้า 50 ใช้น้ำส้มอะไรและปริมาณเท่าไร?"
    },
    {
        "id": "peach_coffee",
        "name_th": "กาแฟพีช (หน้า 48)",
        "name_en": "Peach Coffee",
        "tag": "🍑 หอมกลิ่นผลไม้ (หน้า 48)",
        "badge_color": "#FF8A80",
        "header_bg": "#2A141D",
        "desc": "กาแฟพีชหอมละมุน ใช้ไซรัปพีช โซดา และกาแฟดอยไทยคั่วกลางค่อนเข้ม ให้กลิ่นพีชหวานฉ่ำซาบซ่า",
        "ratio": "ไซรัปพีช 2 ออนซ์ + โซดา 3 ออนซ์ + กาแฟ 1 ช็อต",
        "params": "เสิร์ฟเย็นพร้อมน้ำแข็ง | แต่งชิ้นผลไม้",
        "standard": "กลิ่นหอมพีชฟุ้ง รสเปรี้ยวหวานซ่าผสานรสกาแฟอย่างลงตัว",
        "tip": "คนไซรัปกับโซดาด้านล่างให้เข้ากันก่อน แล้วเทช็อตกาแฟด้านบน",
        "query_sop": "สูตร ส่วนผสม และวิธีทำกาแฟพีชตามคู่มือ (หน้า 48)",
        "query_param": "ส่วนผสมที่ใช้ทำกาแฟพีชในคู่มือหน้า 48 มีอะไรบ้าง?"
    },
    {
        "id": "mint_latte",
        "name_th": "ลาเต้มิ้นท์ (หน้า 49)",
        "name_en": "Mint Latte",
        "tag": "🍃 เมนูพิเศษ (หน้า 49)",
        "badge_color": "#80CBC4",
        "header_bg": "#132522",
        "desc": "ความเย็นสดชื่นของไซรัปมิ้นท์ผสานนมสดและเมล็ดกาแฟคั่วเข้ม 18-20g ให้สัมผัสหวานมัน เย็นชื่นใจ",
        "ratio": "ไซรัปมิ้นท์ + นมสด + กาแฟคั่วเข้ม 18-20g",
        "params": "แก้วเสิร์ฟเย็นพร้อมน้ำแข็ง | ตกแต่งใบมิ้นท์",
        "standard": "หอมกลิ่นมิ้นท์เย็นสดชื่น เนื้อนมนุ่มละมุน กาแฟเข้มข้น",
        "tip": "ตวงเมล็ดกาแฟ 18-20 กรัม บดสดใหม่ก่อนสกัดช็อต",
        "query_sop": "สูตร ส่วนผสม และวิธีทำลาเต้มิ้นท์ตามคู่มือ (หน้า 49)",
        "query_param": "วัตถุดิบสำหรับลาเต้มิ้นท์ในคู่มือหน้า 49 ใช้อะไรบ้าง?"
    },
    {
        "id": "honey_lemon",
        "name_th": "กาแฟน้ำผึ้งมะนาว (หน้า 46)",
        "name_en": "Honey Lemon Coffee",
        "tag": "🍯 หวานอมเปรี้ยว (หน้า 46)",
        "badge_color": "#FFE082",
        "header_bg": "#241A06",
        "desc": "ความลงตัวของน้ำผึ้ง 100% 2 ออนซ์ ผสมน้ำอุ่น 2 ออนซ์ มะนาวสด 4 ลูก และกาแฟดอยไทยคั่วกลางค่อนเข้ม",
        "ratio": "น้ำผึ้ง 2 ออนซ์ + น้ำอุ่น 2 ออนซ์ + มะนาว 4 ลูก + กาแฟ",
        "params": "คนน้ำผึ้งกับน้ำอุ่นให้ละลาย | บีบมะนาวสด | ใส่น้ำแข็ง",
        "standard": "เปรี้ยวหวานสดชื่น ชุ่มคอ ได้ความหอมสดชื่นของมะนาวแท้",
        "tip": "คนน้ำผึ้งกับน้ำอุ่นให้เข้ากันดีก่อนบีบมะนาวและเติมกาแฟ",
        "query_sop": "สูตร ส่วนผสม และวิธีทำกาแฟน้ำผึ้งมะนาวตามคู่มือ (หน้า 46)",
        "query_param": "วัตถุดิบและวิธีทำกาแฟน้ำผึ้งมะนาวในคู่มือหน้า 46"
    }
]


def create_recipe_bubble(item: Dict[str, Any]) -> Dict[str, Any]:
    """
    Creates a single premium Barista Drink Flex Bubble conforming to LINE Flex Message v2 spec.
    """
    header_bg = item.get("header_bg", "#1F130B")
    badge_color = item.get("badge_color", "#D4A373")

    return {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": item.get("header_bg", "#2C1810"),
            "paddingAll": "18px",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"📋 {item.get('tag', 'เมนูบาริสต้า')}",
                            "size": "xxs",
                            "color": badge_color,
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
                    "margin": "sm",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": item.get("name_en", ""),
                    "size": "xxs",
                    "color": "#E0D0C0",
                    "margin": "xs"
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "paddingAll": "16px",
            "backgroundColor": "#FFFFFF",
            "contents": [
                {
                    "type": "text",
                    "text": item.get("desc", ""),
                    "size": "xs",
                    "color": "#4A5568",
                    "wrap": True,
                    "lineSpacing": "3px"
                },
                {
                    "type": "separator",
                    "margin": "md",
                    "color": "#E2E8F0"
                },
                # Specs Box
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "md",
                    "spacing": "xs",
                    "backgroundColor": "#F8FAFC",
                    "cornerRadius": "md",
                    "paddingAll": "10px",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "☕ สัดส่วน:", "size": "xxs", "color": "#718096", "flex": 3},
                                {"type": "text", "text": item.get("ratio", ""), "size": "xxs", "color": "#1A202C", "weight": "bold", "flex": 7, "wrap": True}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "⏱️ พารามิเตอร์:", "size": "xxs", "color": "#718096", "flex": 3},
                                {"type": "text", "text": item.get("params", ""), "size": "xxs", "color": "#2C5282", "weight": "bold", "flex": 7, "wrap": True}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "🎯 มาตรฐาน:", "size": "xxs", "color": "#718096", "flex": 3},
                                {"type": "text", "text": item.get("standard", ""), "size": "xxs", "color": "#22543D", "flex": 7, "wrap": True}
                            ]
                        }
                    ]
                },
                # Tip Box
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "sm",
                    "paddingAll": "8px",
                    "backgroundColor": "#FFFDF5",
                    "cornerRadius": "sm",
                    "borderColor": "#FEEBC8",
                    "borderWidth": "1px",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"💡 เคล็ดลับ: {item.get('tip', '')}",
                            "size": "xxs",
                            "color": "#744210",
                            "wrap": True
                        }
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "paddingAll": "12px",
            "spacing": "xs",
            "backgroundColor": "#FFFFFF",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#8B5A2B",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "📖 ดูวิธีทำ SOP"[:20],
                        "text": item.get("query_sop", "")
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "⚙️ พารามิเตอร์การสกัด"[:20],
                        "text": item.get("query_param", "")
                    }
                }
            ]
        }
    }


def create_recipes_carousel_flex() -> Dict[str, Any]:
    """
    Creates a full Carousel containing 8 verified Barista recipes from documents.pdf.
    """
    bubbles = [create_recipe_bubble(r) for r in RECIPES_DATA]
    return {
        "type": "carousel",
        "contents": bubbles
    }
