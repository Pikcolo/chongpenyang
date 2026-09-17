"""
Test Webhook HTTP API and End-to-End Flex Message generation.
"""

import pytest
from chatbot.interfaces.webhook import app

@pytest.fixture
def client():
    app.config['TESTING'] = True
    with app.test_client() as client:
        yield client

def test_webhook_index(client):
    """Test health check / status endpoint."""
    res = client.get("/")
    assert res.status_code == 200
    data = res.get_json()
    assert data["status"] == "online"
    assert data["recipes_loaded"] >= 10

def test_query_greeting(client):
    """Test 'สวัสดีครับ' returns welcome_flex in under 1.5s."""
    res = client.get("/query?q=สวัสดีครับ")
    assert res.status_code == 200
    data = res.get_json()
    assert data["intent"] == "GREETING"
    assert data["type"] == "welcome_flex"
    assert data["latency_ms"] < 1500

def test_query_out_of_domain_tom_yum(client):
    """Test 'ต้มยำกุ้ง' returns out_of_domain_flex without hallucination."""
    res = client.get("/query?q=แนะนำวิธีทำต้มยำกุ้งน้ำข้นหน่อยครับ")
    assert res.status_code == 200
    data = res.get_json()
    assert data["intent"] == "OUT_OF_DOMAIN"
    assert data["type"] == "out_of_domain_flex"
    assert "flex" in data

def test_query_top5_recommend(client):
    """Test 'ขอ 5 เมนูแนะนำ' returns carousel_flex with 5 items."""
    res = client.get("/query?q=ขอ 5 เมนูแนะนำ")
    assert res.status_code == 200
    data = res.get_json()
    assert data["intent"] == "RECOMMEND_TOP5"
    assert data["type"] == "carousel_flex"
    assert len(data["items"]) == 5

def test_query_recipe_detail(client):
    """Test 'ขอสูตรกาแฟส้ม' returns recipe_detail_flex."""
    res = client.get("/query?q=ขอสูตรกาแฟส้ม")
    assert res.status_code == 200
    data = res.get_json()
    assert data["intent"] == "RECIPE_DETAIL"
    assert data["type"] == "recipe_detail_flex"
    assert "กาแฟส้ม" in data["recipe"]["name_th"]

def test_query_troubleshoot(client):
    """Test 'กาแฟเปรี้ยวฝาดแก้ยังไง' returns troubleshoot_flex."""
    res = client.get("/query?q=กาแฟเปรี้ยวฝาดแก้ยังไง")
    assert res.status_code == 200
    data = res.get_json()
    assert data["intent"] == "TROUBLESHOOT"
    assert data["type"] == "troubleshoot_flex"
