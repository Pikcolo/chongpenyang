"""
LINE Flex Message Citation Bubble for Chongpenyang Barista Assistant.
Renders clean, authoritative reference links to documents.pdf pages.
"""
from typing import List, Dict, Any

def create_citation_flex(citations: List[Dict[str, Any]], query: str = "") -> Dict[str, Any]:
    """
    Renders an elegant Citation Flex Bubble showing PDF page references,
    topic titles, and snippet highlights.
    """
    citation_boxes = []
    for idx, c in enumerate(citations[:4], start=1):
        page = c.get("page", 1)
        topic = c.get("topic", "หลักสูตรบาริสต้ามืออาชีพ")
        preview = c.get("preview", "")

        citation_boxes.append({
            "type": "box",
            "layout": "vertical",
            "backgroundColor": "#FBF8F5",
            "cornerRadius": "sm",
            "paddingAll": "10px",
            "margin": "sm",
            "borderWidth": "1px",
            "borderColor": "#EFE6DD",
            "contents": [
                {
                    "type": "box",
                    "layout": "horizontal",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"📄 หน้า {page}",
                            "weight": "bold",
                            "size": "xs",
                            "color": "#8B5A2B",
                            "flex": 3
                        },
                        {
                            "type": "text",
                            "text": topic[:30] + ("..." if len(topic) > 30 else ""),
                            "weight": "bold",
                            "size": "xs",
                            "color": "#2C1810",
                            "flex": 7,
                            "align": "end"
                        }
                    ]
                },
                {
                    "type": "text",
                    "text": f"\"{preview[:90]}...\"" if preview else "อ้างอิงจากเนื้อหาหลักสูตรบาริสต้ามืออาชีพ",
                    "size": "xxs",
                    "color": "#666666",
                    "margin": "xs",
                    "wrap": True
                }
            ]
        })

    return {
        "type": "bubble",
        "size": "kilo",
        "header": {
            "type": "box",
            "layout": "horizontal",
            "backgroundColor": "#2C1810",
            "paddingAll": "12px",
            "contents": [
                {
                    "type": "text",
                    "text": "📚 แหล่งอ้างอิงคู่มือ (Citations)",
                    "weight": "bold",
                    "size": "xs",
                    "color": "#D4A373"
                }
            ]
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "paddingAll": "12px",
            "contents": citation_boxes or [
                {"type": "text", "text": "คู่มือประกอบการฝึกอบรม หลักสูตร: บาริสต้ามืออาชีพ", "size": "xs", "color": "#555555"}
            ]
        }
    }
