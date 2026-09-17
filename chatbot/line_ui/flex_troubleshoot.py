"""
LINE Flex Message Troubleshoot Bubble for Under vs Over Extraction.
Visual diagnostic card for diagnosing barista espresso flaws.
"""
from typing import Dict, Any

def create_troubleshoot_flex() -> Dict[str, Any]:
    """
    Renders an espresso extraction diagnostic table comparing Under-Extraction vs Over-Extraction.
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
                    "text": "คู่มือวินิจฉัยและแก้ไขรสชาติกาแฟ",
                    "weight": "bold",
                    "size": "lg",
                    "color": "#FFFFFF",
                    "margin": "xs"
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "paddingAll": "18px",
            "contents": [
                # Under Extraction Box
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#FFF5F5",
                    "cornerRadius": "md",
                    "paddingAll": "12px",
                    "borderWidth": "1px",
                    "borderColor": "#FEB2B2",
                    "contents": [
                        {
                            "type": "text",
                            "text": "⚠️ สกัดน้อยเกินไป (Under-Extraction)",
                            "weight": "bold",
                            "size": "sm",
                            "color": "#C53030"
                        },
                        {
                            "type": "text",
                            "text": "• รสชาติ: เปรี้ยวโดด ฝาด จืด ไม่มีบอดี้\n• ลักษณะ: ไหลเร็วเกินไป (< 20 วินาที) ครีม่าซีดบาง\n• สาเหตุ: บดหยาบเกินไป / กาแฟน้อย / น้ำไม่ร้อน / แทมป์เบา\n• การแก้ไข: ปรับเบอร์บดให้ละเอียดขึ้น หรือเพิ่มปริมาณผงกาแฟ",
                            "size": "xxs",
                            "color": "#4A5568",
                            "wrap": True,
                            "margin": "xs"
                        }
                    ]
                },
                # Over Extraction Box
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#FFFAF0",
                    "cornerRadius": "md",
                    "paddingAll": "12px",
                    "margin": "md",
                    "borderWidth": "1px",
                    "borderColor": "#FBD38D",
                    "contents": [
                        {
                            "type": "text",
                            "text": "⚠️ สกัดมากเกินไป (Over-Extraction)",
                            "weight": "bold",
                            "size": "sm",
                            "color": "#C05621"
                        },
                        {
                            "type": "text",
                            "text": "• รสชาติ: ขมไหม้ แห้งติดคอ รสชาติแหลมบาด\n• ลักษณะ: น้ำกาแฟหยดช้า (> 32 วินาที) ครีม่าสีเข้มจัด\n• สาเหตุ: บดละเอียดเกินไป / กาแฟแน่นเกินไป / แทมป์แรงจัด\n• การแก้ไข: ปรับเบอร์บดให้หยาบขึ้น หรือลดแรงแทมป์",
                            "size": "xxs",
                            "color": "#4A5568",
                            "wrap": True,
                            "margin": "xs"
                        }
                    ]
                },
                # Perfect Shot Box
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#F0FFF4",
                    "cornerRadius": "md",
                    "paddingAll": "12px",
                    "margin": "md",
                    "borderWidth": "1px",
                    "borderColor": "#9AE6B4",
                    "contents": [
                        {
                            "type": "text",
                            "text": "✅ สกัดสมบูรณ์ (Perfect Shot)",
                            "weight": "bold",
                            "size": "sm",
                            "color": "#276749"
                        },
                        {
                            "type": "text",
                            "text": "• อุณหภูมิน้ำ: 90 - 96 °C | แรงดัน: 9 - 10 บาร์\n• เวลาสกัด: 20 - 30 วินาที | น้ำกาแฟ: 1 - 1.5 ออนซ์\n• รสชาติ: หวานฉ่ำ กลมกล่อม บอดี้แน่น ครีม่าสีทองหนานุ่ม",
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
                    "action": {
                        "type": "message",
                        "label": "⚙️ วิธีตั้งเบอร์บด",
                        "text": "วิธีปรับเบอร์บดเครื่องบดกาแฟให้เหมาะสม"
                    }
                }
            ]
        }
    }
