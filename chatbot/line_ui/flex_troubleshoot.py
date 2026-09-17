"""
Barista Troubleshooting Diagnostic Flex Card Builder.
Adheres to Criterion 4: LINE Interface & Chat UX.
Explains extraction issues (Under/Over Extraction, Channeling) and actionable adjustments.
"""

from typing import Dict, Any

DIAGNOSTIC_DATA = {
    "under_extraction": {
        "title": "⚠️ ปัญหาการสกัดน้อยเกินไป (Under-Extraction)",
        "badge": "🚨 กาแฟเปรี้ยวฝาด / ไหลเร็วเกินไป",
        "badge_bg": "#ef4444",
        "symptoms": "น้ำกาแฟไหลเร็วพุ่งพรวด (< 20 วินาที), ครีม่ามีสีซีดจางบางเฉียบ, รสชาติเปรี้ยวแหลมฝาดลิ้น ขาดบอดี้และความหวาน",
        "causes": [
            "บดกาแฟหยาบเกินไป (Coarse Grind)",
            "ใส่ปริมาณผงกาแฟน้อยเกินไป (Underdose)",
            "แทมป์กาแฟน้ำหนักเบาเกินไป หน้ากาแฟไม่แน่นพอ"
        ],
        "solutions": [
            "ปรับเบอร์บดให้ละเอียดขึ้น (Finer) ทีละ 1-2 คลิก",
            "เพิ่มปริมาณผงกาแฟ (Dose) เป็น 18 - 20 กรัม",
            "แทมป์ด้วยแรงกดสม่ำเสมอและหน้ากาแฟระนาบเรียบตรง"
        ]
    },
    "over_extraction": {
        "title": "⚠️ ปัญหาการสกัดมากเกินไป (Over-Extraction)",
        "badge": "🚨 กาแฟขมไหม้ / หยดไหลช้า",
        "badge_bg": "#b91c1c",
        "symptoms": "น้ำกาแฟหยดติ๋งๆ ช้าผิดปกติ (> 32 วินาที), ครีม่าสีน้ำตาลเข้มจัดเกือบดำ มีจุดด่างดำไหม้, รสชาติขมไหม้ แห้งติดคอ",
        "causes": [
            "บดกาแฟละเอียดแน่นเกินไป (Too Fine)",
            "ใส่ปริมาณผงกาแฟมากเกินไป (Overdose)",
            "แทมป์น้ำหนักกดแน่นมากเกินไป หรือหน้า Shower Screen อุดตัน"
        ],
        "solutions": [
            "ปรับเบอร์บดให้หยาบขึ้น (Coarser) เล็กน้อย",
            "ลดปริมาณผงกาแฟลงให้อยู่ในสเปก Basket (เช่น 18 กรัม)",
            "Purge ล้างหัวชงและเช็ดทำความสะอาดหน้า Shower Screen"
        ]
    },
    "channeling": {
        "title": "⚠️ ปัญหาการเกิด Channeling",
        "badge": "🚨 น้ำกาแฟไหลลัดเลาะไม่สม่ำเสมอ",
        "badge_bg": "#f97316",
        "symptoms": "น้ำกาแฟพุ่งกระจายจาก Portafilter ไหลไม่รวมศูนย์ รสชาติทั้งเปรี้ยวและขมปนกันในแก้วเดียว",
        "causes": [
            "ผงกาแฟจับตัวเป็นก้อนใน Basket",
            "กดแทมป์เอียง ทำให้หน้ากาแฟมีความหนาบางไม่เท่ากัน",
            "เคาะด้ามชงแรงหลังแทมป์ทำให้ก้อนกาแฟแตกตัวจากขอบ"
        ],
        "solutions": [
            "ใช้อุปกรณ์เกลี่ยผงกาแฟ (WDT) กระจายก้อนกาแฟให้ร่วน",
            "แทมป์ให้หน้าเรียบขนานกับขอบ Basket เสมอ 90 องศา",
            "ห้ามเคาะด้ามชงหลังแทมป์เสร็จแล้วเด็ดขาด"
        ]
    }
}

def build_troubleshoot_flex(trouble_type: str = "under_extraction") -> Dict[str, Any]:
    """Builds a diagnostic troubleshooting card."""
    data = DIAGNOSTIC_DATA.get(trouble_type, DIAGNOSTIC_DATA["under_extraction"])

    cause_items = []
    for c in data["causes"]:
        cause_items.append({
            "type": "box",
            "layout": "horizontal",
            "spacing": "xs",
            "contents": [
                {"type": "text", "text": "❌", "size": "xxs", "flex": 0},
                {"type": "text", "text": c, "size": "xs", "color": "#7f1d1d", "wrap": True, "flex": 1}
            ]
        })

    sol_items = []
    for s in data["solutions"]:
        sol_items.append({
            "type": "box",
            "layout": "horizontal",
            "spacing": "xs",
            "contents": [
                {"type": "text", "text": "✅", "size": "xxs", "flex": 0},
                {"type": "text", "text": s, "size": "xs", "color": "#14532d", "wrap": True, "flex": 1}
            ]
        })

    bubble = {
        "type": "bubble",
        "size": "mega",
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "paddingAll": "20px",
            "contents": [
                # Badge
                {
                    "type": "box",
                    "layout": "baseline",
                    "contents": [
                        {"type": "text", "text": data["badge"], "size": "xs", "color": "#ffffff", "weight": "bold"}
                    ],
                    "backgroundColor": data["badge_bg"],
                    "cornerRadius": "md",
                    "paddingAll": "6px",
                    "alignItems": "center",
                    "justifyContent": "center"
                },
                # Title
                {
                    "type": "text",
                    "text": data["title"],
                    "weight": "bold",
                    "size": "md",
                    "color": "#1c1917",
                    "wrap": True
                },
                # Symptoms
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#fef2f2",
                    "cornerRadius": "md",
                    "paddingAll": "10px",
                    "contents": [
                        {"type": "text", "text": "🔍 ลักษณะที่สังเกตได้:", "weight": "bold", "size": "xxs", "color": "#991b1b"},
                        {"type": "text", "text": data["symptoms"], "size": "xs", "color": "#450a0a", "wrap": True}
                    ]
                },
                # Causes
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "xs",
                    "contents": [
                        {"type": "text", "text": "📌 สาเหตุหลัก:", "weight": "bold", "size": "xs", "color": "#991b1b"},
                        *cause_items
                    ]
                },
                # Solutions
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#f0fdf4",
                    "cornerRadius": "md",
                    "paddingAll": "10px",
                    "spacing": "xs",
                    "contents": [
                        {"type": "text", "text": "🛠️ วิธีแก้ไขตามคู่มือบาริสต้า:", "weight": "bold", "size": "xs", "color": "#166534"},
                        *sol_items
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
                        "label": "📖 ดูตัวแปร Perfect Shot",
                        "text": "ตัวแปรมาตรฐานการสกัดเอสเพรสโซ่"
                    }
                }
            ]
        }
    }
    return bubble
