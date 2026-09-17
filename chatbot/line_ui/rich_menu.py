"""
LINE Rich Menu Generator and Payload Configurator for Chongpenyang Barista Assistant.
Generates an official 2500x1686 6-grid Rich Menu image and configures LINE API payload.
"""
import os
import json
import logging
from PIL import Image, ImageDraw, ImageFont

logger = logging.getLogger(__name__)

RICH_MENU_IMG_PATH = "chatbot/web/static/images/rich_menu_line.jpg"

BARISTA_MENU_ITEMS = [
    # Row 1
    {
        "title": "เมล็ด & การคั่ว",
        "sub": "MOD_01: สายพันธุ์, Agtron, 5 เบอร์บด",
        "icon": "🌱",
        "bg": "#2C1810",
        "accent": "#D4A373",
        "text": "ความรู้เรื่องเมล็ดกาแฟ สายพันธุ์ ระดับการคั่ว Agtron และเบอร์บด (MOD_01)"
    },
    {
        "title": "สกัด Perfect Shot",
        "sub": "MOD_02: 9-10 บาร์, 90-96°C, 20-30s",
        "icon": "☕",
        "bg": "#3E2723",
        "accent": "#E6CCB2",
        "text": "สูตรและเทคนิคการสกัด Perfect Shot เอสเพรสโซ่"
    },
    {
        "title": "ลาเต้อาร์ต",
        "sub": "MOD_03: Microfoam 60-65°C & ลายเท",
        "icon": "🥛",
        "bg": "#2C1810",
        "accent": "#D4A373",
        "text": "เทคนิคการสตีมนมและทำลาเต้อาร์ต"
    },
    # Row 2
    {
        "title": "13 เมนูเครื่องดื่ม SOP",
        "sub": "MOD_04: สูตรกาแฟร้อน & กาแฟเย็น",
        "icon": "🍹",
        "bg": "#4E342E",
        "accent": "#F5EBE0",
        "text": "เมนูเครื่องดื่ม"
    },
    {
        "title": "วินิจฉัย Under / Over",
        "sub": "MOD_02: แก้รสชาติ & Channeling",
        "icon": "🔬",
        "bg": "#2C1810",
        "accent": "#D4A373",
        "text": "วิเคราะห์รสชาติ"
    },
    {
        "title": "ควิซ & ใบงานบาริสต้า",
        "sub": "MOD_05: แบบทดสอบ, Checklist, เฉลย",
        "icon": "📝",
        "bg": "#3E2723",
        "accent": "#E6CCB2",
        "text": "แบบทดสอบวัดระดับความรู้บาริสต้าในคู่มือ (MOD_05) มีอะไรบ้าง?"
    }
]

def prepare_rich_menu_image(
    source_path: str = RICH_MENU_IMG_PATH,
    output_path: str = "chatbot/web/static/images/rich_menu_line.jpg",
    force_generate: bool = False
) -> str:
    """
    Prepares a LINE-compliant 2500x1686 image (strictly under 1MB limit).
    Uses the custom rich_menu_barista.png image resized to 2500x1686 via LANCZOS.
    Falls back to procedural generation only if custom image is missing.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if not force_generate and os.path.exists(source_path):
        try:
            with Image.open(source_path) as img:
                img_rgb = img.convert("RGB")
                img_resized = img_rgb.resize((2500, 1686), Image.Resampling.LANCZOS)
                img_resized.save(output_path, format="JPEG", quality=92, optimize=True)
                logger.info(f"Custom rich menu image processed and saved to {output_path}")
                return output_path
        except Exception as e:
            logger.warning(f"Failed to process custom rich menu image {source_path}: {e}, falling back to generator")

    # Generate fresh procedural image matching updated 6 modules
    temp_png = "chatbot/web/static/images/rich_menu_generated.png"
    generate_rich_menu_image(temp_png)
    with Image.open(temp_png) as img:
        img_rgb = img.convert("RGB")
        img_rgb.save(output_path, format="JPEG", quality=92, optimize=True)
    return output_path


def generate_rich_menu_image(output_path: str = RICH_MENU_IMG_PATH) -> str:
    """
    Generates a 2500x1686 PNG image with 6 rich interactive cards for LINE Rich Menu.
    """
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    width, height = 2500, 1686
    img = Image.new("RGB", (width, height), color="#1A0F0A")
    draw = ImageDraw.Draw(img)

    cols, rows = 3, 2
    cell_w = width // cols
    cell_h = height // rows

    # Font setup
    try:
        font_title = ImageFont.truetype("tahoma.ttf", 68)
        font_sub = ImageFont.truetype("tahoma.ttf", 40)
        font_icon = ImageFont.truetype("seguiemj.ttf", 110)
    except Exception:
        try:
            font_title = ImageFont.truetype("arial.ttf", 68)
            font_sub = ImageFont.truetype("arial.ttf", 40)
            font_icon = font_title
        except Exception:
            font_title = ImageFont.load_default()
            font_sub = font_title
            font_icon = font_title

    idx = 0
    for r in range(rows):
        for c in range(cols):
            x1 = c * cell_w
            y1 = r * cell_h
            x2 = x1 + cell_w
            y2 = y1 + cell_h

            item = BARISTA_MENU_ITEMS[idx]
            idx += 1

            # Card background with border
            draw.rectangle([x1 + 12, y1 + 12, x2 - 12, y2 - 12], fill=item["bg"], outline=item["accent"], width=5)

            # Draw texts
            center_x = x1 + cell_w // 2

            # Icon
            try:
                draw.text((center_x, y1 + 220), item["icon"], font=font_icon, fill="#FFFFFF", anchor="mm")
            except Exception:
                pass

            # Title
            draw.text((center_x, y1 + 460), item["title"], font=font_title, fill=item["accent"], anchor="mm")

            # Subtitle
            draw.text((center_x, y1 + 560), item["sub"], font=font_sub, fill="#C0C0C0", anchor="mm")

    img.save(output_path, format="PNG", quality=95)
    return output_path

def get_rich_menu_payload() -> dict:
    """
    Returns the LINE Rich Menu configuration payload corresponding to 6 grids.
    """
    width, height = 2500, 1686
    cell_w = width // 3
    cell_h = height // 2

    areas = []
    idx = 0
    for r in range(2):
        for c in range(3):
            item = BARISTA_MENU_ITEMS[idx]
            idx += 1
            areas.append({
                "bounds": {
                    "x": c * cell_w,
                    "y": r * cell_h,
                    "width": cell_w,
                    "height": cell_h
                },
                "action": {
                    "type": "message",
                    "text": item["text"]
                }
            })

    return {
        "size": {"width": width, "height": height},
        "selected": True,
        "name": "Chongpenyang Barista Rich Menu",
        "chatBarText": "☕ เมนูบาริสต้า",
        "areas": areas
    }

