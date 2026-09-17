"""
Detailed Barista Recipe Flex Card Builder.
Adheres to Criterion 4: LINE Interface & Chat UX (15% Weight).
Provides comprehensive recipe specifications, extraction parameters, and step-by-step instructions.
"""

from typing import Dict, Any

def build_recipe_detail_flex(recipe: Dict[str, Any]) -> Dict[str, Any]:
    """Generates a detailed recipe bubble flex message."""
    name_th = recipe.get("name_th", "สูตรกาแฟ")
    name_en = recipe.get("name_en", "")
    image_url = recipe.get("image_url", "https://images.unsplash.com/photo-1510591509098-f4fdc6d0ff04?w=700&auto=format&fit=crop&q=80")
    dose = recipe.get("dose_g", 18)
    yield_ml = recipe.get("yield_ml", 36)
    temp = recipe.get("temp_c", "90 - 95°C")
    pressure = recipe.get("pressure_bar", "9 บาร์")
    brew_time = recipe.get("brew_time_s", "25 - 30 วินาที")
    grind = recipe.get("grind_size", "ละเอียด")
    roast = recipe.get("roast_level", "คั่วกลาง")
    ingredients = recipe.get("ingredients", [])
    steps = recipe.get("steps", [])
    tips = recipe.get("tips", "ควบคุมตัวแปรให้สม่ำเสมอ")

    # Format ingredient items
    ing_contents = []
    for ing in ingredients[:5]:
        ing_contents.append({
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "contents": [
                {"type": "text", "text": "•", "size": "xs", "color": "#78350f", "flex": 0},
                {"type": "text", "text": str(ing), "size": "xs", "color": "#44403c", "wrap": True, "flex": 1}
            ]
        })

    # Format step items
    step_contents = []
    for idx, st in enumerate(steps[:5], 1):
        step_contents.append({
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "contents": [
                {"type": "text", "text": f"{idx}.", "size": "xs", "color": "#b45309", "weight": "bold", "flex": 0},
                {"type": "text", "text": str(st), "size": "xs", "color": "#292524", "wrap": True, "flex": 1}
            ]
        })

    bubble = {
        "type": "bubble",
        "size": "mega",
        "hero": {
            "type": "image",
            "url": image_url,
            "size": "full",
            "aspectRatio": "20:13",
            "aspectMode": "cover"
        },
        "body": {
            "type": "box",
            "layout": "vertical",
            "spacing": "md",
            "paddingAll": "20px",
            "contents": [
                # Title
                {
                    "type": "box",
                    "layout": "vertical",
                    "contents": [
                        {"type": "text", "text": name_th, "weight": "bold", "size": "lg", "color": "#78350f", "wrap": True},
                        {"type": "text", "text": name_en, "size": "xs", "color": "#a8a29e", "wrap": True}
                    ]
                },
                {"type": "separator"},
                # Barista Parameters Grid
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#fef3c7",
                    "cornerRadius": "md",
                    "paddingAll": "12px",
                    "spacing": "xs",
                    "contents": [
                        {
                            "type": "text",
                            "text": "📊 ตัวแปรมาตรฐานการสกัด (Barista Specs)",
                            "weight": "bold",
                            "size": "xs",
                            "color": "#92400e"
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": f"ผงกาแฟ: {dose}g", "size": "xxs", "color": "#78350f", "flex": 1},
                                {"type": "text", "text": f"น้ำกาแฟ: {yield_ml}ml", "size": "xxs", "color": "#78350f", "flex": 1}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": f"อุณหภูมิ: {temp}", "size": "xxs", "color": "#78350f", "flex": 1},
                                {"type": "text", "text": f"เวลา: {brew_time}", "size": "xxs", "color": "#78350f", "flex": 1}
                            ]
                        },
                        {
                            "type": "box",
                            "layout": "horizontal",
                            "contents": [
                                {"type": "text", "text": f"แรงดัน: {pressure}", "size": "xxs", "color": "#78350f", "flex": 1},
                                {"type": "text", "text": f"การบด: {grind}", "size": "xxs", "color": "#78350f", "flex": 1}
                            ]
                        }
                    ]
                },
                # Ingredients
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "xs",
                    "contents": [
                        {"type": "text", "text": "🥣 ส่วนผสมและอุปกรณ์", "weight": "bold", "size": "sm", "color": "#1c1917"},
                        *ing_contents
                    ]
                },
                # Steps
                {
                    "type": "box",
                    "layout": "vertical",
                    "spacing": "xs",
                    "contents": [
                        {"type": "text", "text": "☕ ขั้นตอนการทำ", "weight": "bold", "size": "sm", "color": "#1c1917"},
                        *step_contents
                    ]
                },
                # Barista Tip Box
                {
                    "type": "box",
                    "layout": "vertical",
                    "backgroundColor": "#f5f5f4",
                    "cornerRadius": "md",
                    "paddingAll": "10px",
                    "contents": [
                        {"type": "text", "text": "💡 เคล็ดลับบาริสต้า (Pro Tip):", "weight": "bold", "size": "xxs", "color": "#0369a1"},
                        {"type": "text", "text": str(tips), "size": "xxs", "color": "#334155", "wrap": True}
                    ]
                }
            ]
        },
        "footer": {
            "type": "box",
            "layout": "horizontal",
            "spacing": "sm",
            "paddingAll": "14px",
            "contents": [
                {
                    "type": "button",
                    "style": "secondary",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "🎲 สุ่มเมนูอื่น",
                        "text": "ขอ 5 เมนูแนะนำ"
                    },
                    "flex": 1
                },
                {
                    "type": "button",
                    "style": "primary",
                    "color": "#0284c7",
                    "height": "sm",
                    "action": {
                        "type": "message",
                        "label": "⚠️ แก้ปัญหาสกัด",
                        "text": "กาแฟเปรี้ยวฝาดแก้ยังไง"
                    },
                    "flex": 1
                }
            ]
        }
    }
    return bubble
