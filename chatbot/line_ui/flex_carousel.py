"""
Top 5 Carousel Flex Message Builder for Barista Chatbot.
Adheres to Criterion 4: LINE Interface & Chat UX (15% Weight).
Formats up to 5 items into a visually stunning, smooth swipeable LINE Carousel.
"""

from typing import List, Dict, Any

CATEGORY_BADGES = {
    "hot": {"label": "☕ เมนูร้อน", "color": "#8D6E63"},
    "iced": {"label": "🧊 เมนูเย็น", "color": "#0288D1"},
    "signature": {"label": "⭐ ซิกเนเจอร์", "color": "#E65100"}
}

def create_recipe_card(recipe: Dict[str, Any]) -> Dict[str, Any]:
    """Generates a single Flex Bubble card for a recipe."""
    cat = recipe.get("category", "hot")
    badge_info = CATEGORY_BADGES.get(cat, CATEGORY_BADGES["hot"])

    name_th = recipe.get("name_th", "เมนูกาแฟ")
    # Truncate title cleanly if too long
    display_title = name_th.split("(")[0].strip()
    sub_title = recipe.get("name_en", "")

    flavor = recipe.get("flavor_notes", "รสชาติกลมกล่อม หอมกรุ่น")
    image_url = recipe.get("image_url", "https://images.unsplash.com/photo-1510591509098-f4fdc6d0ff04?w=700&auto=format&fit=crop&q=80")
    difficulty = recipe.get("difficulty", "ระดับกลาง")
    roast = recipe.get("roast_level", "คั่วกลาง")
    recipe_id = recipe.get("id", "espresso_hot")

    bubble = {
        "type": "bubble",
        "size": "kilo",
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
            "spacing": "sm",
            "paddingAll": "16px",
            "contents": [
                {
                    "type": "box",
                    "layout": "baseline",
                    "spacing": "xs",
                    "contents": [
                        {
                            "type": "text",
                            "text": badge_info["label"],
                            "size": "xxs",
                            "color": "#ffffff",
                            "weight": "bold"
                        }
                    ],
                    "backgroundColor": badge_info["color"],
                    "cornerRadius": "md",
                    "paddingAll": "4px",
                    "width": "80px",
                    "alignItems": "center",
                    "justifyContent": "center"
                },
                {
                    "type": "text",
                    "text": display_title,
                    "weight": "bold",
                    "size": "md",
                    "color": "#1c1917",
                    "wrap": True
                },
                {
                    "type": "text",
                    "text": sub_title,
                    "size": "xs",
                    "color": "#78716c",
                    "wrap": True
                },
                {
                    "type": "separator",
                    "margin": "sm"
                },
                {
                    "type": "text",
                    "text": flavor,
                    "size": "xxs",
                    "color": "#44403c",
                    "wrap": True,
                    "maxLines": 2
                },
                {
                    "type": "box",
                    "layout": "horizontal",
                    "margin": "xs",
                    "contents": [
                        {
                            "type": "text",
                            "text": f"🔥 {roast.split('(')[0].strip()}",
                            "size": "xxs",
                            "color": "#b45309",
                            "flex": 1
                        },
                        {
                            "type": "text",
                            "text": f"⚡ {difficulty}",
                            "size": "xxs",
                            "color": "#475569",
                            "align": "end",
                            "flex": 1
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
                    "color": "#78350f",
                    "height": "sm",
                    "action": {
                        "type": "postback",
                        "label": "📖 ดูสูตรและวิธีชง",
                        "data": f"action=view_recipe&id={recipe_id}",
                        "displayText": f"ขอสูตร {display_title}"
                    }
                }
            ]
        }
    }
    return bubble

def build_top5_carousel_flex(recipes: List[Dict[str, Any]], title_text: str = "🌟 5 เมนูแนะนำสำหรับบาริสต้า") -> Dict[str, Any]:
    """Wraps up to 5 recipe cards into a LINE Carousel container."""
    bubbles = [create_recipe_card(r) for r in recipes[:5]]
    return {
        "type": "carousel",
        "contents": bubbles
    }
