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
from chatbot.line_ui.quick_replies import get_barista_quick_replies, get_quick_reply_list
from chatbot.line_ui.flex_welcome import create_welcome_flex
from chatbot.line_ui.flex_carousel import create_recipes_carousel_flex
from chatbot.line_ui.flex_troubleshoot import create_troubleshoot_flex
from chatbot.line_ui.flex_citation import create_citation_flex

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
    return jsonify({"quick_replies": get_quick_reply_list()})

@app.route("/api/flex/carousel", methods=["GET"])
def api_flex_carousel():
    """Returns the popular coffee recipes carousel flex schema."""
    return jsonify({"carousel": create_recipes_carousel_flex()})

@app.route("/api/flex/troubleshoot", methods=["GET"])
def api_flex_troubleshoot():
    """Returns extraction troubleshoot flex schema."""
    return jsonify({"flex": create_troubleshoot_flex()})

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
    """LINE Messaging API webhook handler."""
    if not handler:
        return "LINE credentials not configured", 500

    signature = request.headers.get("X-Line-Signature", "")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    except Exception as e:
        print(f"Error handling webhook: {e}")
        abort(500)

    return "OK"

if handler:
    @handler.add(MessageEvent, message=TextMessage)
    def handle_line_text_message(event):
        user_text = event.message.text.strip()
        user_id = event.source.user_id

        # 1. Build Quick Reply items for LINE
        qr_payload = get_barista_quick_replies()
        quick_reply_obj = QuickReply(
            items=[
                QuickReplyButton(
                    action=MessageAction(
                        label=item["action"]["label"],
                        text=item["action"]["text"]
                    )
                )
                for item in qr_payload["items"]
            ]
        )

        # 2. Check for Rich Menu / Shortcut Intents
        clean_text = user_text.lower()

        # Intent A: Popular Drinks Carousel
        if any(w in clean_text for w in ["เมนูเครื่องดื่ม", "แนะนำสูตรเมนู", "สูตรเมนูยอดนิยม", "carousel"]):
            flex_content = create_recipes_carousel_flex()
            flex_msg = FlexSendMessage(
                alt_text="🍹 แนะนำสูตรเมนูเครื่องดื่มยอดนิยมตามคู่มือ",
                contents=flex_content,
                quick_reply=quick_reply_obj
            )
            line_bot_api.reply_message(event.reply_token, flex_msg)
            return

        # Intent B: Extraction Diagnosis / Troubleshoot Card
        if any(w in clean_text for w in ["วิเคราะห์รสชาติ", "แก้อาการ", "รสเปรี้ยวเกินไป", "ขมเกินไป", "under", "over"]):
            flex_content = create_troubleshoot_flex()
            flex_msg = FlexSendMessage(
                alt_text="🔬 คู่มือวินิจฉัยและแก้ไขรสชาติกาแฟ (Under vs Over Extraction)",
                contents=flex_content,
                quick_reply=quick_reply_obj
            )
            line_bot_api.reply_message(event.reply_token, flex_msg)
            return

        # Intent C: Standard RAG Question Answering
        output = rag_chain.answer_question(user_text, session_id=user_id)
        reply_text = output["answer"]

        # Limit to 4900 chars (LINE limit is 5000)
        if len(reply_text) > 4900:
            reply_text = reply_text[:4900] + "..."

        text_msg = TextSendMessage(
            text=reply_text,
            quick_reply=quick_reply_obj
        )
        line_bot_api.reply_message(event.reply_token, text_msg)


def run_server():
    print(f"🌐 Starting Chongpenyang Barista AI Server on port {settings.PORT}...")
    print(f"📱 Web Simulator & Inspector: http://localhost:{settings.PORT}")
    print(f"🔗 LINE Webhook URL: http://localhost:{settings.PORT}/callback")
    app.run(host=settings.HOST, port=settings.PORT, debug=False)

if __name__ == "__main__":
    run_server()
