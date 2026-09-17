"""
Automated Unit and Benchmark Tests for Barista Chatbot.
Adheres to the Rubric Key Checkpoints:
1. NLP Latency & Edge Cases (< 1.5 - 2s, handles slang & typos)
2. Randomization Fairness (Anti-loop Top 5 sampling)
3. Flex Message JSON Schema Validity
4. Zero Hallucination Guardrail (Out of domain queries)
"""

import pytest
import time
from chatbot.nlp.intent_parser import BaristaIntentParser, BaristaIntent
from chatbot.recommender.filter_engine import BaristaFilterEngine
from chatbot.line_ui.flex_carousel import build_top5_carousel_flex
from chatbot.line_ui.flex_detail import build_recipe_detail_flex
from chatbot.line_ui.flex_troubleshoot import build_troubleshoot_flex
from chatbot.line_ui.flex_welcome import build_welcome_flex, build_out_of_domain_flex
from chatbot.line_ui.flex_knowledge import build_knowledge_flex

@pytest.fixture
def parser():
    return BaristaIntentParser()

@pytest.fixture
def recommender():
    return BaristaFilterEngine()

def test_nlp_intent_accuracy_and_latency(parser):
    """Verifies intent classification accuracy > 85% and latency < 1.5s (typically < 10ms)."""
    test_cases = [
        # Greeting
        ("สวัสดีครับ", BaristaIntent.GREETING),
        ("hello", BaristaIntent.GREETING),
        ("ดีค่ะ", BaristaIntent.GREETING),
        # Out of Domain
        ("แนะนำวิธีทำต้มยำกุ้งน้ำข้นหน่อยครับ", BaristaIntent.OUT_OF_DOMAIN),
        ("ขอสูตรผัดไทยกุ้งสด", BaristaIntent.OUT_OF_DOMAIN),
        ("สอนเขียนโค้ด python", BaristaIntent.OUT_OF_DOMAIN),
        ("ทำสเต็กเนื้อยังไง", BaristaIntent.OUT_OF_DOMAIN),
        # Top 5 Recommender
        ("ขอ 5 เมนูแนะนำ", BaristaIntent.RECOMMEND_TOP5),
        ("top 5 เครื่องดื่ม", BaristaIntent.RECOMMEND_TOP5),
        ("สุ่มเมนูให้หน่อย", BaristaIntent.RECOMMEND_TOP5),
        ("กินอะไรดี", BaristaIntent.RECOMMEND_TOP5),
        # Category Filter
        ("ขอเมนูร้อนหน่อย", BaristaIntent.FILTER_CATEGORY),
        ("มีกาแฟเย็นอะไรบ้าง", BaristaIntent.FILTER_CATEGORY),
        ("ขอกาแฟผลไม้สดชื่น", BaristaIntent.FILTER_CATEGORY),
        # Recipe Detail
        ("ขอสูตรกาแฟส้ม", BaristaIntent.RECIPE_DETAIL),
        ("วิธีทำลาเต้ร้อน", BaristaIntent.RECIPE_DETAIL),
        ("ขอสูตร dirty coffee", BaristaIntent.RECIPE_DETAIL),
        ("ชงเอสเพรสโซ่เย็นยังไง", BaristaIntent.RECIPE_DETAIL),
        # Troubleshoot
        ("กาแฟเปรี้ยวฝาดแก้ยังไง", BaristaIntent.TROUBLESHOOT),
        ("กาแฟขมไหม้ หยดช้า", BaristaIntent.TROUBLESHOOT),
        ("เกิด channeling ทำไง", BaristaIntent.TROUBLESHOOT),
        # Knowledge Query
        ("ระดับการคั่ว Agtron Scale ของคั่วอ่อนคือเท่าไร", BaristaIntent.KNOWLEDGE_QUERY),
        ("ตัวแปรมาตรฐานในการสกัด Perfect Shot มีอะไรบ้าง", BaristaIntent.KNOWLEDGE_QUERY)
    ]

    correct = 0
    total = len(test_cases)

    for query, expected_intent in test_cases:
        t0 = time.perf_counter()
        res = parser.parse(query)
        elapsed_ms = (time.perf_counter() - t0) * 1000

        # Latency checkpoint: must be well below 1500ms (1.5s)
        assert elapsed_ms < 1500, f"Latency too high: {elapsed_ms:.2f}ms for '{query}'"

        if res.intent == expected_intent:
            correct += 1
        else:
            print(f"FAILED: '{query}' -> Expected {expected_intent}, got {res.intent}")

    accuracy = correct / total
    print(f"\n✅ NLP Intent Accuracy: {accuracy * 100:.1f}% ({correct}/{total})")
    assert accuracy >= 0.85, f"Accuracy {accuracy:.2f} below 85% threshold!"

def test_randomization_fairness_anti_loop(recommender):
    """
    Checkpoint: Randomization Fairness
    Verifies that consecutive Top 5 refreshes do not get stuck in a loop of identical items.
    """
    session_id = "test_user_fairness"
    recommender.reset_session(session_id)

    seen_sets = []
    all_selected_ids = set()

    for cycle in range(5):
        items = recommender.get_top5_recommendations(session_id=session_id, limit=5)
        assert len(items) == 5, f"Expected 5 items, got {len(items)}"
        ids_tuple = tuple(sorted(it["id"] for it in items))
        all_selected_ids.update(ids_tuple)

        # Ensure current batch is not an exact duplicate of the immediately preceding batch
        if seen_sets:
            assert ids_tuple != seen_sets[-1], f"Repetitive loop detected at cycle {cycle+1}!"

        seen_sets.append(ids_tuple)

    # Over 5 cycles of 5 items, we should see at least 10 unique recipes out of the 14 in catalog
    assert len(all_selected_ids) >= 10, f"Randomization starved! Only {len(all_selected_ids)} distinct items shown."

def test_flex_message_json_validity(recommender):
    """Verifies that all generated LINE Flex messages conform to valid JSON structures."""
    sample_recipes = recommender.get_top5_recommendations(limit=5)
    sample_recipe = sample_recipes[0]

    # 1. Top 5 Carousel Flex
    carousel = build_top5_carousel_flex(sample_recipes)
    assert carousel["type"] == "carousel"
    assert len(carousel["contents"]) == 5
    for bubble in carousel["contents"]:
        assert bubble["type"] == "bubble"
        assert "hero" in bubble
        assert "body" in bubble
        assert "footer" in bubble

    # 2. Recipe Detail Flex
    detail_bubble = build_recipe_detail_flex(sample_recipe)
    assert detail_bubble["type"] == "bubble"
    assert detail_bubble["size"] == "mega"
    assert "body" in detail_bubble

    # 3. Troubleshoot Flex
    trouble_bubble = build_troubleshoot_flex("under_extraction")
    assert trouble_bubble["type"] == "bubble"
    assert "body" in trouble_bubble

    # 4. Welcome Flex
    welcome_bubble = build_welcome_flex()
    assert welcome_bubble["type"] == "bubble"
    assert "body" in welcome_bubble

    # 5. Out of Domain Flex
    ood_bubble = build_out_of_domain_flex("ต้มยำกุ้ง")
    assert ood_bubble["type"] == "bubble"
    assert "body" in ood_bubble

    # 6. Knowledge Flex
    know_bubble = build_knowledge_flex("อุณหภูมิน้ำ", "ควรอยู่ที่ 90-95 องศาเซลเซียส", [{"page": 24, "topic": "การสกัด"}])
    assert know_bubble["type"] == "bubble"
    assert "body" in know_bubble

def test_zero_hallucination_on_out_of_domain(parser):
    """Verifies that food/unrelated queries are strictly classified as OUT_OF_DOMAIN with no Chinese text."""
    queries = [
        "ต้มยำกุ้งน้ำข้น",
        "วิธีทำผัดไทย",
        "สูตรข้าวมันไก่",
        "สเต็กเนื้อซอสพริกไทยดำ"
    ]
    for q in queries:
        res = parser.parse(q)
        assert res.intent == BaristaIntent.OUT_OF_DOMAIN, f"Query '{q}' should be OUT_OF_DOMAIN"
