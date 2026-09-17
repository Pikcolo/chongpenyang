"""
LINE Flex Message Welcome Bubble for Chongpenyang Barista Assistant.
Renders an elegant barista-themed introduction card showcasing the 5 Official Modules.
"""
from typing import Dict, Any

def create_welcome_flex() -> Dict[str, Any]:
    """
    Renders an elegant barista onboarding card with quick-action buttons.
    """
    return {
        "type": "bubble",
        "size": "giga",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "CHONGPENYANG BARISTA AI ☕",
                    "weight": "bold",
                    "size": "xs",
                    "color": "#D4A373",
                    "letterSpacing": "2px"
                },
                {
                    "type": "text",
                    "text": "คู่มือบาริสต้ามืออาชีพ (5 โมดูล)",
                    "weight": "bold",
                    "size": "lg",
                    "color": "#FFFFFF",
                    "margin": "sm"
                },
                {
                    "type": "text",
                    "text": "ระบบผู้ช่วยอัจฉริยะ Production Hybrid RAG",
                    "size": "xs",
                    "color": "#E6CCB2",
                    "margin": "xs"
                }
            ],
            "backgroundColor": "#2C1810",
            "paddingAll": "18px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "paddingAll": "16px",
            "contents": [
                {
                    "type": "text",
                    "text": "ยินดีต้อนรับสู่คู่มือบาริสต้ามาตรฐานสากล!",
                    "weight": "bold",
                    "size": "sm",
                    "color": "#2C1810"
                },
                {
                    "type": "text",
                    "text": "ระบบพร้อมให้คำปรึกษาและค้นหาข้อมูลอย่างแม่นยำตาม 5 โมดูลของคู่มือ:",
                    "size": "xxs",
                    "color": "#666666",
                    "wrap": True,
                    "margin": "xs"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "sm",
                    "spacing": "xs",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "🌱 MOD_01:", "size": "xxs", "color": "#8B5A2B", "weight": "bold", "flex": 3},
                                {"type": "text", "text": "เมล็ดกาแฟ, สายพันธุ์, การคั่ว (Agtron 80-70), เบอร์บด (น.3-19)", "size": "xxs", "color": "#444444", "flex": 8, "wrap": True}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "⚙️ MOD_02:", "size": "xxs", "color": "#8B5A2B", "weight": "bold", "flex": 3},
                                {"type": "text", "text": "การสกัด Perfect Shot, แก้ Under/Over, Channeling (น.20-31)", "size": "xxs", "color": "#444444", "flex": 8, "wrap": True}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "🥛 MOD_03:", "size": "xxs", "color": "#8B5A2B", "weight": "bold", "flex": 3},
                                {"type": "text", "text": "ประวัติศาสตร์และศาสตร์ลาเต้อาร์ต, Microfoam 60-65°C (น.32-36)", "size": "xxs", "color": "#444444", "flex": 8, "wrap": True}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "🍹 MOD_04:", "size": "xxs", "color": "#8B5A2B", "weight": "bold", "flex": 3},
                                {"type": "text", "text": "ขั้นตอนปฏิบัติงาน SOP 13 เมนูร้อนและเย็น (น.37-50)", "size": "xxs", "color": "#444444", "flex": 8, "wrap": True}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "📝 MOD_05:", "size": "xxs", "color": "#8B5A2B", "weight": "bold", "flex": 3},
                                {"type": "text", "text": "แบบทดสอบวัดระดับบาริสต้า, เช็กลิสต์ทักษะและเฉลย (น.51-53)", "size": "xxs", "color": "#444444", "flex": 8, "wrap": True}
                            ]
                        }
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "xs",
            "paddingAll": "12px",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#8B5A2B",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "🍹 แนะนำสูตรเมนูเครื่องดื่ม (SOP)",
                        "text": "แนะนำสูตรเมนูเครื่องดื่มยอดนิยมตามคู่มือ"
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "🔬 วินิจฉัยรสชาติกาแฟ (Under/Over)",
                        "text": "วิธีแก้ปัญหากาแฟรสชาติเปรี้ยวเกินไปหรือขมเกินไป"
                    }
                }
            ]
        }
    }
