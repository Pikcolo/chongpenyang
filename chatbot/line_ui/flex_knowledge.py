"""
Knowledge & Citations Flex Card Builder for RAG Answers.
Formats complex technical barista questions cleanly into structured LINE Flex messages.
"""

from typing import Dict, Any, List

def build_knowledge_flex(question: str, answer_text: str, citations: List[Dict[str, Any]] = None) -> Dict[str, Any]:
    """Wraps RAG text answer and page citations into a clean, modern Flex card."""
    citations = citations or []

    # Clean markdown asterisks from answer text for clean LINE rendering
    clean_answer = answer_text.replace("**", "").replace("##", "").strip()

    citation_boxes = []
    if citations:
        for cit in citations[:3]:
            page = cit.get("page", 0)
            topic = cit.get("topic", "คู่มือบาริสต้ามืออาชีพ")
            citation_boxes.append({
                "type": "box",
                "layout": "horizontal",
                "spacing": "xs",
                "contents": [
                    {"type": "text", "text": "📄", "size": "xxs", "flex": 0},
                    {"type": "text", "text": f"หน้า {page} — {topic}", "size": "xxs", "color": "#0369a1", "wrap": True, "flex": 1}
                ]
            })

    body_contents = [
        {
            "type": "box",
            "layout": "baseline",
            "contents": [
                {"type": "text", "text": "📖 ข้อมูลจากหลักสูตรบาริสต้ามืออาชีพ", "size": "xxs", "color": "#ffffff", "weight": "bold"}
            ],
            "backgroundColor": "#0284c7",
            "cornerRadius": "md",
            "paddingAll": "4px",
            "alignItems": "center",
            "justifyContent": "center"
        },
        {
            "type": "text",
            "text": question,
            "weight": "bold",
            "size": "sm",
            "color": "#0f172a",
            "wrap": True
        },
        {"type": "separator"},
        {
            "type": "text",
            "text": clean_answer,
            "size": "xs",
            "color": "#334155",
            "wrap": True
        }
    ]

    if citation_boxes:
        body_contents.append({"type": "separator", "margin": "md"})
        body_contents.append({
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#f0f9ff",
            "cornerRadius": "md",
            "paddingAll": "8px",
            "spacing": "xs",
            "contents": [
                {"type": "text", "text": "📚 แหล่งอ้างอิงในเอกสาร (Citations):", "size": "xxs", "color": "#0369a1", "weight": "bold"},
                *citation_boxes
            ]
        })

    bubble = {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "sm",
            "paddingAll": "18px",
            "contents": body_contents
        },
        "footer": {
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "paddingAll": "12px",
            "contents": [
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "🎲 5 เมนูแนะนำ",
                        "text": "ขอ 5 เมนูแนะนำ"
                    },
                    "flex": 1
                },
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#78350f",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "☕ สูตรเอสเพรสโซ่",
                        "text": "ขอสูตรเอสเพรสโซ่ร้อน"
                    },
                    "flex": 1
                }
            ]
        }
    }
    return bubble
