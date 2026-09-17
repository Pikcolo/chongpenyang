"""
LINE Flex Message Troubleshoot Bubble for Under vs Over Extraction and Channeling.
Visual diagnostic card for diagnosing barista espresso extraction flaws (MOD_02).
"""
from typing import Dict, Any

def create_troubleshoot_flex() -> Dict[str, Any]:
    """
    Renders an espresso extraction diagnostic table comparing:
    - Under-Extraction
    - Over-Extraction
    - Channeling
    - Perfect Shot
    """
    return {
        "type": "bubble",
        "size": "giga",
        "header": {
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#1A0F0A",
            "paddingAll": "18px",
            "contents": [
                {
                    "type": "text",
                    "text": "🔬 ESPRESSO EXTRACTION DIAGNOSIS",
                    "weight": "bold",
                    "size": "xs",
                    "color": "#D4A373",
                    "letterSpacing": "1px"
                },
                {
                    "type": "text",
                    "text": "คู่มือวินิจฉัยและแก้ไขรสชาติกาแฟ (MOD_02)",
                    "weight": "bold",
                    "size": "md",
                    "color": "#FFFFFF",
                    "margin": "xs"
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "paddingAll": "16px",
            "contents": [
                # 1. Under Extraction Box
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#FFF5F5",
                    "cornerRadius": "md",
                    "paddingAll": "10px",
                    "borderWidth": "1px",
                    "borderColor": "#FEB2B2",
                    "contents": [
                        {
                            "type": "text",
                            "text": "⚠️ สกัดน้อยเกินไป (Under-Extraction)",
                            "weight": "bold",
                            "size": "xs",
                            "color": "#C53030"
                        },
                        {
                            "type": "text",
                            "text": "• รสชาติ: เปรี้ยวโดด ฝาด จืด ไม่มีบอดี้\n• การไหล: ไหลเร็วผิดปกติ (< 20 วินาที) ครีม่าซีดบาง\n• สาเหตุ: บดหยาบเกินไป / กาแฟน้อย (Under-dose) / แทมป์เบา\n• การแก้ไข: ปรับเบอร์บดให้ละเอียดขึ้น หรือเพิ่มปริมาณผงกาแฟ",
                            "size": "xxs",
                            "color": "#4A5568",
                            "wrap": True,
                            "margin": "xs"
                        }
                    ]
                },
                # 2. Over Extraction Box
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#FFFAF0",
                    "cornerRadius": "md",
                    "paddingAll": "10px",
                    "margin": "sm",
                    "borderWidth": "1px",
                    "borderColor": "#FBD38D",
                    "contents": [
                        {
                            "type": "text",
                            "text": "⚠️ สกัดมากเกินไป (Over-Extraction)",
                            "weight": "bold",
                            "size": "xs",
                            "color": "#C05621"
                        },
                        {
                            "type": "text",
                            "text": "• รสชาติ: ขมไหม้ แห้งติดคอ รสฝาดแหลมบาด\n• การไหล: น้ำกาแฟหยดช้า ไม่สม่ำเสมอ (> 30 วินาที) ครีม่าสีเข้มจัด\n• สาเหตุ: บดละเอียดเกินไป / กาแฟแน่นเกินไป (Over-dose) / แทมป์แน่นจัด\n• การแก้ไข: ปรับเบอร์บดให้หยาบขึ้น หรือลดปริมาณผงกาแฟลง",
                            "size": "xxs",
                            "color": "#4A5568",
                            "wrap": True,
                            "margin": "xs"
                        }
                    ]
                },
                # 3. Channeling Box
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#FAF5FF",
                    "cornerRadius": "md",
                    "paddingAll": "10px",
                    "margin": "sm",
                    "borderWidth": "1px",
                    "borderColor": "#D6BCFA",
                    "contents": [
                        {
                            "type": "text",
                            "text": "⚡ น้ำลัดช่องก้อนกาแฟ (Channeling)",
                            "weight": "bold",
                            "size": "xs",
                            "color": "#6B46C1"
                        },
                        {
                            "type": "text",
                            "text": "• รสชาติ: สับสน เปรี้ยวฝาดปนขมไหม้ในแก้วเดียวกัน\n• การไหล: น้ำพุ่งกระเด็น หรือไหลไม่สม่ำเสมอทั่วทั้ง Basket\n• สาเหตุ: ผงกาแฟจับก้อน / แทมป์เอียง / เคาะด้ามชงหลังแทมป์\n• การแก้ไข: เกลี่ยผงกาแฟด้วยเข็ม WDT, แทมป์ระนาบ 90°, ห้ามเคาะด้าม",
                            "size": "xxs",
                            "color": "#4A5568",
                            "wrap": True,
                            "margin": "xs"
                        }
                    ]
                },
                # 4. Perfect Shot Box
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#F0FFF4",
                    "cornerRadius": "md",
                    "paddingAll": "10px",
                    "margin": "sm",
                    "borderWidth": "1px",
                    "borderColor": "#9AE6B4",
                    "contents": [
                        {
                            "type": "text",
                            "text": "✅ สกัดสมบูรณ์แบบ (Espresso Perfect Shot)",
                            "weight": "bold",
                            "size": "xs",
                            "color": "#276749"
                        },
                        {
                            "type": "text",
                            "text": "• อุณหภูมิน้ำ: 90 - 96 °C | แรงดันปั๊ม: 9 - 10 บาร์\n• เวลาสกัด: 20 - 30 วินาที | ปริมาณน้ำกาแฟ: 1 - 1.5 ออนซ์ (30-45 มล.)\n• รสชาติ: หวานฉ่ำ กลมกล่อม บอดี้แน่น ครีม่าสีทองหนานุ่ม",
                            "size": "xxs",
                            "color": "#2F855A",
                            "wrap": True,
                            "margin": "xs"
                        }
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "paddingAll": "10px",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#8B5A2B",
                    "height": "sm",
                    "flex": 1,
                    "action": {
                        "type": "message",
                        "label": "⚙️ ตั้งเบอร์บด",
                        "text": "วิธีปรับเบอร์บดเครื่องบดกาแฟให้เหมาะสม"
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "flex": 1,
                    "action": {
                        "type": "message",
                        "label": "🛡️ แก้ Channeling",
                        "text": "Channeling คืออะไร เกิดจากอะไร และป้องกันอย่างไร?"
                    }
                }
            ]
        }
    }
