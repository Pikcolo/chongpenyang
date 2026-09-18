"""
Production LINE Bot Webhook Server and REST API for SmartDoc Barista Hybrid RAG.
Provides:
1. Web Testing Simulator & Real-time RAG Inspector at '/'
2. LINE Messaging API Webhook at '/callback' with Flex Messages & Quick Replies
3. Telemetry REST API at '/api/chat', '/api/quick_replies', '/api/flex/*'
"""

import os
import sys
import time
import pickle
from pathlib import Path
from flask import Flask, request, abort, jsonify, render_template

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

from chatbot.config import settings
from chatbot.retrieval.vector_store import VectorStoreManager
from chatbot.retrieval.bm25_retriever import BM25Retriever
from chatbot.retrieval.reranker import CrossEncoderReranker
from chatbot.retrieval.dynamic_retriever import DynamicHybridRetriever
from chatbot.generation.guardrails import GuardrailManager
from chatbot.generation.rag_chain import BaristaRAGChain

# LINE UI components
from chatbot.line_ui.flex_welcome import create_welcome_flex
from chatbot.line_ui.flex_carousel import create_recipes_carousel_flex
from chatbot.line_ui.flex_troubleshoot import create_troubleshoot_flex
from chatbot.line_ui.quick_replies import get_line_sdk_quick_reply, get_quick_reply_list

# Configure Flask App with Web Simulator templates & static folder
WEB_DIR = Path(__file__).resolve().parent.parent / "web"
app = Flask(
    __name__,
    template_folder=str(WEB_DIR / "templates"),
    static_folder=str(WEB_DIR / "static")
)

# Initialize LINE Bot API handlers
line_bot_api = None
handler = None

try:
    from linebot import LineBotApi, WebhookHandler
    from linebot.exceptions import InvalidSignatureError
    from linebot.models import (
        MessageEvent, TextMessage, TextSendMessage,
        FlexSendMessage, QuickReply, QuickReplyButton, MessageAction
    )

    if settings.CHANNEL_ACCESS_TOKEN and settings.CHANNEL_SECRET:
        line_bot_api = LineBotApi(settings.CHANNEL_ACCESS_TOKEN)
        handler = WebhookHandler(settings.CHANNEL_SECRET)
        print("✅ LINE Messaging API initialized.")
    else:
        print("ℹ️ LINE credentials not provided; running in Web Simulator mode.")
except Exception as e:
    print(f"⚠️ LINE Bot SDK Notice: {e}")

# Initialize RAG Pipeline Singletons
print("🚀 Initializing Production RAG Engine...")
vector_mgr = VectorStoreManager(store_type=settings.VECTOR_STORE_TYPE)
vector_mgr.load_existing()

cache_path = Path(settings.CHROMA_PATH).parent / "documents_cache.pkl"
if cache_path.exists():
    with open(cache_path, "rb") as f:
        child_docs = pickle.load(f)
else:
    child_docs = []

bm25 = BM25Retriever(child_docs)
reranker = CrossEncoderReranker(settings.RERANKER_MODEL) if settings.RERANKER_ENABLED else None
retriever = DynamicHybridRetriever(vector_mgr, bm25, reranker)
guardrails = GuardrailManager()
rag_chain = BaristaRAGChain(retriever, guardrails)
print("✅ Production RAG Engine online and ready.")


# ==========================================
# Web Simulator & Telemetry Endpoints
# ==========================================

@app.route("/", methods=["GET"])
def index():
    """Renders the Barista AI Web Simulator & Inspector UI."""
    return render_template("index.html")

@app.route("/api/quick_replies", methods=["GET"])
def api_quick_replies():
    """Returns preset quick-reply chips for web UI."""
    q = request.args.get("q", "").strip()
    return jsonify({"quick_replies": get_quick_reply_list(user_query=q)})

@app.route("/health", methods=["GET"])
def health():
    """Health check endpoint for container and uptime monitoring."""
    return jsonify({
        "status": "healthy",
        "service": "Chongpenyang Barista Assistant",
        "model": settings.OLLAMA_MODEL,
        "retriever": settings.VECTOR_STORE_TYPE
    })

@app.route("/api/flex/carousel", methods=["GET"])
def api_flex_carousel():
    """Returns the popular coffee recipes carousel flex schema."""
    return jsonify({"carousel": create_recipes_carousel_flex()})

@app.route("/api/flex/troubleshoot", methods=["GET"])
def api_flex_troubleshoot():
    """Returns extraction troubleshoot flex schema."""
    bubble = create_troubleshoot_flex()
    return jsonify({"flex": bubble, "bubble": bubble})

@app.route("/api/chat", methods=["POST"])
def api_chat():
    """Interactive endpoint for the Web Simulator with RAG telemetry."""
    data = request.get_json() or {}
    message = data.get("message", "").strip()
    session_id = data.get("session_id", "web_user")

    if not message:
        return jsonify({"error": "Empty message"}), 400

    start_time = time.time()
    output = rag_chain.answer_question(message, session_id=session_id)
    latency_ms = round((time.time() - start_time) * 1000)

    contexts = output.get("contexts", [])
    max_score = max([c.get("score", 0.0) for c in contexts]) if contexts else 0.85

    telemetry = {
        "model": settings.OLLAMA_MODEL,
        "retrieval": f"{settings.VECTOR_STORE_TYPE.upper()} + BM25 + RRF",
        "reranker": "Cross-Encoder (mmarco-mMiniLMv2)" if settings.RERANKER_ENABLED else "None",
        "dynamic_k": output.get("dynamic_k", 5),
        "confidence": max_score,
        "latency_ms": latency_ms,
        "chunks": [
            {
                "page": c.get("page", 1),
                "topic": c.get("topic_title", "เนื้อหาคู่มือ"),
                "score": c.get("score", 0.0),
                "content": c.get("content", "")[:180] + "..."
            }
            for c in contexts[:4]
        ]
    }

    return jsonify({
        "question": message,
        "reply_text": output["answer"],
        "citations": output.get("citations", []),
        "quick_replies": get_quick_reply_list(user_query=message, reply_text=output["answer"]),
        "telemetry": telemetry
    })

@app.route("/query", methods=["GET", "POST"])
def query_legacy():
    """Legacy test endpoint."""
    if request.method == "POST":
        data = request.get_json() or {}
        q = data.get("question") or data.get("q", "")
    else:
        q = request.args.get("q", "")
    if not q:
        return jsonify({"error": "Missing 'q'"}), 400
    out = rag_chain.answer_question(q)
    return jsonify(out)


# ==========================================
# LINE Messaging API Webhook
# ==========================================

@app.route("/callback", methods=["POST"])
def callback():
    """LINE Messaging API webhook handler with asynchronous event processing."""
    if not handler:
        return "LINE credentials not configured", 500

    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    # Validate signature synchronously before returning 200
    try:
        if not handler.parser.signature_validator.validate(body, signature):
            abort(400)
    except Exception:
        abort(400)

    # Process events in background thread to immediately return 200 OK to LINE/Cloudflare
    import threading
    def _async_handle(body_data, sig):
        try:
            handler.handle(body_data, sig)
        except Exception as err:
            print(f"⚠️ Error in async event handler: {err}")

    threading.Thread(target=_async_handle, args=(body, signature), daemon=True).start()

    return "OK"

def show_line_loading_animation(chat_id: str, seconds: int = 25):
    """Triggers LINE's native thinking/loading animation in the user's chat screen asynchronously."""
    if not settings.CHANNEL_ACCESS_TOKEN or not chat_id:
        print(f"⚠️ Cannot show loading animation: missing token or chat_id (chat_id={chat_id})")
        return

    import threading
    def _call():
        try:
            import requests
            url = "https://api.line.me/v2/bot/chat/loading/start"
            headers = {
                "Authorization": f"Bearer {settings.CHANNEL_ACCESS_TOKEN}",
                "Content-Type": "application/json"
            }
            payload = {"chatId": chat_id, "loadingSeconds": min(max(5, seconds), 60)}
            res = requests.post(url, headers=headers, json=payload, timeout=5)
            print(f"⏳ [LINE API] Loading Animation started for {chat_id}: HTTP {res.status_code}")
        except Exception as e:
            print(f"⚠️ [LINE API] Failed to trigger loading animation: {e}")

    threading.Thread(target=_call, daemon=True).start()

if handler:
    @handler.add(MessageEvent, message=TextMessage)
    def handle_line_text_message(event):
        user_text = event.message.text.strip()
        user_id = getattr(event.source, "user_id", None) or getattr(event.source, "sender_id", None)
        clean_text = user_text.lower()

        # 🟢 Show native LINE loading/typing indicator (the 3 animated dots) immediately
        print(f"📩 [LINE Incoming] user_id='{user_id}' | text: '{user_text}'")
        if user_id:
            show_line_loading_animation(user_id, seconds=25)

        import re

        # Check if message contains question indicators
        question_words = ["?", "คือ", "อะไร", "ใคร", "ที่ไหน", "เมื่อไหร่", "อย่างไร", "ทำไม", "เท่าไร", "เท่าใด", "สูตร", "วิธี", "ช่วย", "ทำยังไง", "ขอ", "แนะนำ", "ต่างกัน", "แก้อาการ", "แก้", "กี่", "ไหม", "มั้ย", "แชมป์", "ชนะ", "ลาย"]
        has_question = any(qw in clean_text for qw in question_words) or len(clean_text) > 25

        # Pure greeting: only if user is NOT asking a question and only saying hello
        is_pure_greeting = False
        if not has_question:
            thai_greetings = ["สวัสดี", "สวัสดีครับ", "สวัสดีค่ะ", "หวัดดี", "หวัดดีครับ", "หวัดดีค่ะ", "ดีครับ", "ดีค่ะ", "ดีจ้า", "เริ่มต้น", "start", "เริ่ม"]
            if clean_text in thai_greetings:
                is_pure_greeting = True
            elif re.fullmatch(r'(hi|hello|hey|greetings)[\s!.]*', clean_text):
                is_pure_greeting = True

        # Intent A: Welcome Card & Table of Contents (5 Modules)
        # Only trigger if user explicitly asks for table of contents, module overview, or pure greeting
        is_toc_request = clean_text in ["สารบัญ", "5 โมดูล", "ภาพรวมหลักสูตร", "คู่มือบาริสต้ามืออาชีพ", "เริ่มต้น", "start", "help", "เมนูหลัก"] or \
                         (not has_question and any(w in clean_text for w in ["ดูสารบัญ", "ขอสารบัญ", "สรุป 5 โมดูล", "ภาพรวมหลักสูตร", "เปิดเมนู", "สารบัญ 5 โมดูล"]))

        if is_toc_request or is_pure_greeting:
            flex_content = create_welcome_flex()
            quick_reply = get_line_sdk_quick_reply(user_text, "สารบัญ 5 โมดูลหลักสูตรบาริสต้ามืออาชีพ")
            flex_msg = FlexSendMessage(
                alt_text="☕ คู่มือบาริสต้ามืออาชีพ (5 โมดูล) - Chongpenyang Barista AI",
                contents=flex_content,
                quick_reply=quick_reply
            )
            line_bot_api.reply_message(event.reply_token, flex_msg)
            return

        # Intent B: Popular Drinks Carousel (Only on explicit menu/carousel request)
        is_carousel_request = clean_text in ["เมนูเครื่องดื่ม", "แนะนำสูตรเมนู", "สูตรเมนูยอดนิยม", "carousel"] or \
                              (not has_question and any(w in clean_text for w in ["ดูเมนูเครื่องดื่ม", "ขอสูตรเมนูยอดนิยม", "สไลด์เมนู", "เมนูกาแฟยอดนิยม"]))

        if is_carousel_request:
            flex_content = create_recipes_carousel_flex()
            quick_reply = get_line_sdk_quick_reply(user_text, "สูตรเมนูเครื่องดื่มยอดนิยมตามคู่มือ")
            flex_msg = FlexSendMessage(
                alt_text="🍹 แนะนำสูตรเมนูเครื่องดื่มยอดนิยมตามคู่มือ SOP",
                contents=flex_content,
                quick_reply=quick_reply
            )
            line_bot_api.reply_message(event.reply_token, flex_msg)
            return

        # Intent C: Extraction Diagnosis / Troubleshoot Card (Only on explicit diagnose overview request)
        is_troubleshoot_request = clean_text in ["วิเคราะห์รสชาติ", "แก้อาการ", "troubleshoot", "วินิจฉัยรสชาติ"] or \
                                  (not has_question and any(w in clean_text for w in ["วิเคราะห์รสชาติกาแฟ", "การวินิจฉัยการสกัด", "การ์ดแก้อาการ"]))

        if is_troubleshoot_request:
            flex_content = create_troubleshoot_flex()
            quick_reply = get_line_sdk_quick_reply(user_text, "วิเคราะห์รสชาติและแก้ไขการสกัด")
            flex_msg = FlexSendMessage(
                alt_text="🔬 คู่มือวินิจฉัยและแก้ไขรสชาติกาแฟ (Under vs Over Extraction & Channeling)",
                contents=flex_content,
                quick_reply=quick_reply
            )
            line_bot_api.reply_message(event.reply_token, flex_msg)
            return

        # Intent D: Standard RAG Question Answering (Always answer questions with RAG)
        output = rag_chain.answer_question(user_text, session_id=user_id)
        raw_answer = output["answer"]

        if not output.get("guardrail_triggered", False):
            display_q = user_text if len(user_text) <= 50 else (user_text[:47] + "...")
            reply_text = (
                f"☕ Chongpenyang Barista AI\n"
                f"คู่มือประกอบการฝึกอบรม หลักสูตรบาริสต้ามืออาชีพ\n"
                f"━━━━━━━━━━━━━━━━━━━━\n"
                f"❓ {display_q}\n\n"
                f"{raw_answer}"
            )
        else:
            reply_text = raw_answer

        # Limit to 4900 chars (LINE limit is 5000)
        if len(reply_text) > 4900:
            reply_text = reply_text[:4900] + "..."

        quick_reply = get_line_sdk_quick_reply(user_text, raw_answer)
        text_msg = TextSendMessage(text=reply_text, quick_reply=quick_reply)
        line_bot_api.reply_message(event.reply_token, text_msg)


def run_server():
    print(f"🌐 Starting Chongpenyang Barista AI Server on port {settings.PORT}...")
    print(f"📱 Web Simulator & Inspector: http://localhost:{settings.PORT}")
    print(f"🔗 LINE Webhook URL: http://localhost:{settings.PORT}/callback")
    app.run(host=settings.HOST, port=settings.PORT, debug=False)

if __name__ == "__main__":
    run_server()
