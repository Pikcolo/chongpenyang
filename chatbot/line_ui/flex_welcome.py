"""
LINE Flex Message Welcome Bubble for Chongpenyang Barista Assistant.
Renders an elegant barista-themed introduction card.
"""
from typing import Dict, Any

def create_welcome_flex() -> Dict[str, Any]:
    """
    Renders an elegant barista onboarding card with quick-action buttons.
    """
    return {
        "type": "bubble",
        "size": "mega",
        "header": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "CHONGPENYANG BARISTA AI",
                    "weight": "bold",
                    "size": "xs",
                    "color": "#D4A373",
                    "letterSpacing": "2px"
                },
                {
                    "type": "text",
                    "text": "คู่มือบาริสต้ามืออาชีพ ☕",
                    "weight": "bold",
                    "size": "xl",
                    "color": "#FFFFFF",
                    "margin": "sm"
                },
                {
                    "type": "text",
                    "text": "ระบบผู้ช่วยอัจฉริยะ Production-Grade Hybrid RAG",
                    "size": "xs",
                    "color": "#E6CCB2",
                    "margin": "xs"
                }
            ],
            "backgroundColor": "#2C1810",
            "paddingAll": "20px"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "contents": [
                {
                    "type": "text",
                    "text": "ยินดีต้อนรับสู่คู่มือฝึกอบรมบาริสต้ามืออาชีพ!",
                    "weight": "bold",
                    "size": "md",
                    "color": "#212121"
                },
                {
                    "type": "text",
                    "text": "สอบถามสูตรเครื่องดื่ม เทคนิคการสกัด Perfect Shot การปรับเบอร์บด และการแก้ปัญหา Over/Under Extraction ตามมาตรฐานสากลได้ทันที",
                    "size": "sm",
                    "color": "#666666",
                    "wrap": True,
                    "margin": "md"
                },
                {
                    "type": "separator",
                    "margin": "lg",
                    "color": "#EEEEEE"
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "margin": "md",
                    "spacing": "sm",
                    "contents": [
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "🎯 อุณหภูมิสกัด:", "size": "xs", "color": "#888888", "flex": 4},
                                {"type": "text", "text": "90 - 96 °C", "size": "xs", "color": "#2C1810", "weight": "bold", "flex": 5}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "⚡ แรงดันสกัด:", "size": "xs", "color": "#888888", "flex": 4},
                                {"type": "text", "text": "9 - 10 บาร์ (Bar)", "size": "xs", "color": "#2C1810", "weight": "bold", "flex": 5}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": "⏱️ เวลาสกัด:", "size": "xs", "color": "#888888", "flex": 4},
                                {"type": "text", "text": "20 - 30 วินาที", "size": "xs", "color": "#2C1810", "weight": "bold", "flex": 5}
                            ]
                        }
                    ]
                }
            ],
            "paddingAll": "20px"
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#8B5A2B",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "☕ สูตร Perfect Shot",
                        "text": "สูตรและเทคนิคการสกัด Perfect Shot เอสเพรสโซ่"
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "🍊 แนะนำเมนูเครื่องดื่ม",
                        "text": "แนะนำสูตรเมนูเครื่องดื่มยอดนิยมตามคู่มือ"
                    }
                }
            ],
            "paddingAll": "15px"
        }
    }
