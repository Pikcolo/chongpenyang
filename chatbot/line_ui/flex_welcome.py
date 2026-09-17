"""
Welcome & Out-of-Domain Guardrail Flex Message Builders.
Provides polite, helpful, and strictly on-brand barista messaging with Zero Hallucination.
"""

from typing import Dict, Any

def build_welcome_flex() -> Dict[str, Any]:
    """Generates an aesthetic welcome card for Barista Chatbot."""
    bubble = {
        "type": "bubble",
        "size": "mega",
        "hero": {
            "type": "image",
            "url": "https://images.unsplash.com/photo-1495474472287-4d71bcdd2085?w=700&auto=format&fit=crop&q=80",
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "paddingAll": "20px",
            "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                        {"type": "text", "text": "☕ CHONGPENYANG BARISTA AI", "size": "xxs", "color": "#ffffff", "weight": "bold"}
                    ],
                    "backgroundColor": "#78350f",
                    "cornerRadius": "md",
                    "paddingAll": "4px",
                    "alignItems": "center",
                    "justifyContent": "center"
                },
                {
                    "type": "text",
                    "text": "สวัสดีครับ! ยินดีต้อนรับสู่ผู้ช่วยฝึกอบรมบาริสต้า",
                    "weight": "bold",
                    "size": "md",
                    "color": "#1c1917",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": "ผมคือระบบช่วยสอนและค้นหาสูตรกาแฟ อ้างอิงจากหลักสูตรบาริสต้ามืออาชีพ คุณสามารถพิมพ์ถามสูตร, ขอคำแนะนำ 5 เมนูเด็ด, หรือปรึกษาปัญหาการสกัดได้ทันทีครับ",
                    "size": "xs",
                    "color": "#57534e",
                    "wrap": True
                },
                {"type": "separator", "margin": "md"},
                {
                    "type": "text",
                    "text": "✨ เมนูด่วนแนะนำ:",
                    "weight": "bold",
                    "size": "xxs",
                    "color": "#b45309"
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "paddingAll": "16px",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#78350f",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "🎲 5 เมนูแนะนำ (Top 5)",
                        "text": "ขอ 5 เมนูแนะนำ"
                    }
                },
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "⚠️ กาแฟเปรี้ยว/ขม แก้ยังไง",
                        "text": "กาแฟเปรี้ยวฝาดแก้ยังไง"
                    }
                }
            ]
        }
    }
    return bubble

def build_out_of_domain_flex(query: str = "") -> Dict[str, Any]:
    """Generates a strictly guarded Zero Hallucination rejection card for out-of-domain queries."""
    bubble = {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "paddingAll": "20px",
            "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                        {"type": "text", "text": "🛡️ ขอบเขตการให้บริการ (Out of Domain)", "size": "xxs", "color": "#ffffff", "weight": "bold"}
                    ],
                    "backgroundColor": "#64748b",
                    "cornerRadius": "md",
                    "paddingAll": "4px",
                    "alignItems": "center",
                    "justifyContent": "center"
                },
                {
                    "type": "text",
                    "text": "ขออภัยครับ คำถามนี้อยู่นอกเหนือขอบเขต",
                    "weight": "bold",
                    "size": "md",
                    "color": "#1e293b",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": "ระบบนี้ถูกฝึกฝนมาเพื่อเป็น 'คู่มือประกอบการฝึกอบรม หลักสูตรบาริสต้ามืออาชีพ' โดยเฉพาะ ซึ่งครอบคลุมเฉพาะเรื่องเมล็ดกาแฟ, เทคนิคการสกัด Espresso, การสตีมนม, การบำรุงรักษาเครื่อง และสูตรเครื่องดื่มกาแฟเท่านั้นครับ",
                    "size": "xs",
                    "color": "#475569",
                    "wrap": True
                },
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#f8fafc",
                    "cornerRadius": "md",
                    "paddingAll": "10px",
                    "contents": [
                        {"type": "text", "text": "💡 ลองเลือกถามเรื่องเหล่านี้แทน:", "weight": "bold", "size": "xxs", "color": "#0369a1"},
                        {"type": "text", "text": "• สูตรกาแฟส้มสด หรือ Dirty Coffee\n• วิธีแก้ปัญหากาแฟเปรี้ยวฝาด / กาแฟขมไหม้\n• อุณหภูมิน้ำและแรงดันในการสกัดเอสเพรสโซ่\n• อุณหภูมิที่เหมาะสมในการสตีมนม", "size": "xxs", "color": "#334155", "wrap": True}
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "paddingAll": "12px",
            "contents": [
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#78350f",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "☕ ดูเมนูแนะนำ",
                        "text": "ขอ 5 เมนูแนะนำ"
                    },
                    "flex": 1
                }
            ]
        }
    }
    return bubble
