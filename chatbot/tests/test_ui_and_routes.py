"""
Unit and Integration tests for LINE UI, Flex Message Carousel, Quick Replies, and Webhook Routes.
Verifies compliance with LINE Messaging API constraints:
- Quick Reply label <= 20 characters
- Quick Reply items <= 13
- Carousel bubble count <= 12
"""
import pytest
from chatbot.line_ui.flex_carousel import create_recipes_carousel_flex, RECIPES_DATA
from chatbot.line_ui.flex_troubleshoot import create_troubleshoot_flex
from chatbot.line_ui.quick_replies import (
    get_barista_quick_replies,
    get_quick_reply_list,
    select_contextual_chips,
    EXTRACTION_QUICK_REPLIES,
    MILK_LATTE_ART_QUICK_REPLIES,
    RECIPES_QUICK_REPLIES,
    BEANS_ROAST_GRIND_QUICK_REPLIES,
    DEFAULT_BARISTA_QUICK_REPLIES
)
from chatbot.interfaces.webhook import app

@pytest.fixture
def client():
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def test_flex_carousel_structure():
    """Verify that Flex Carousel contains 8 verified recipe bubbles conforming to LINE spec."""
    carousel = create_recipes_carousel_flex()
    assert carousel["type"] == "carousel"
    contents = carousel["contents"]
    assert len(contents) == 8
    assert len(contents) <= 12  # LINE Carousel limit is 12 bubbles

    for bubble in contents:
        assert bubble["type"] == "bubble"
        assert bubble["size"] == "mega"
        assert "header" in bubble
        assert "body" in bubble
        assert "footer" in bubble

        # Verify buttons in footer
        footer_buttons = bubble["footer"]["contents"]
        assert len(footer_buttons) >= 1
        for btn in footer_buttons:
            assert btn["type"] == "button"
            action = btn["action"]
            assert action["type"] == "message"
            assert len(action["label"]) <= 20, f"Button label too long: {action['label']}"
            assert len(action["text"]) > 0


def test_flex_troubleshoot_structure():
    """Verify that Troubleshoot bubble conforms to LINE spec."""
    bubble = create_troubleshoot_flex()
    assert bubble["type"] == "bubble"
    assert "header" in bubble
    assert "body" in bubble
    assert "footer" in bubble

    footer_buttons = bubble["footer"]["contents"]
    for btn in footer_buttons:
        assert len(btn["action"]["label"]) <= 20


def test_quick_replies_line_constraints():
    """Verify all quick reply pools strictly conform to LINE API character limits (<= 20 chars)."""
    all_pools = [
        EXTRACTION_QUICK_REPLIES,
        MILK_LATTE_ART_QUICK_REPLIES,
        RECIPES_QUICK_REPLIES,
        BEANS_ROAST_GRIND_QUICK_REPLIES,
        DEFAULT_BARISTA_QUICK_REPLIES
    ]

    for pool in all_pools:
        for chip in pool:
            label = chip["label"]
            assert len(label) <= 20, f"Quick Reply label '{label}' exceeds 20 characters (len={len(label)})"
            assert len(chip["text"]) > 0


def test_quick_replies_payload_generation():
    """Verify dynamic quick replies generator truncates and limits to 12 items."""
    test_queries = [
        ("สวัสดีครับ", "ยินดีต้อนรับสู่คู่มือบาริสต้ามืออาชีพ"),
        ("กาแฟ Under-Extraction ทำไมเปรี้ยว", "น้ำกาแฟไหลเร็วเกินไป เกิดจากการบดหยาบ"),
        ("สตีมนมทำลาเต้อาร์ตลายทิวลิป", "อุณหภูมิ 60-65 องศาเซลเซียส เพื่อให้เกิดไมโครโฟม"),
        ("สูตรกาแฟส้มทำยังไง", "ใช้น้ำส้มแท้ 120ml และเอสเพรสโซ่ 2 ช็อต"),
        ("สายพันธุ์อาราบิก้าและโรบัสต้าต่างกันอย่างไร", "อาราบิก้าปลูกบนดอยสูง กลิ่นหอมละมุน")
    ]

    for q, r in test_queries:
        payload = get_barista_quick_replies(q, r)
        assert "items" in payload
        items = payload["items"]
        assert len(items) <= 13, f"Exceeded max 13 items: {len(items)}"
        for it in items:
            lbl = it["action"]["label"]
            assert len(lbl) <= 20, f"Label exceeds 20 chars: {lbl}"


def test_health_endpoint(client):
    """Test /health endpoint."""
    res = client.get("/health")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "healthy"
    assert data["service"] == "Chongpenyang Barista Assistant"


def test_api_flex_carousel_endpoint(client):
    """Test /api/flex/carousel endpoint."""
    res = client.get("/api/flex/carousel")
    assert res.status_code == 200
    data = res.get_json()
    assert "carousel" in data
    assert len(data["carousel"]["contents"]) == 8


def test_api_flex_troubleshoot_endpoint(client):
    """Test /api/flex/troubleshoot endpoint."""
    res = client.get("/api/flex/troubleshoot")
    assert res.status_code == 200
    data = res.get_json()
    assert "bubble" in data
    assert data["bubble"]["type"] == "bubble"
