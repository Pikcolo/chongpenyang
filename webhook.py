import os
import sys
from flask import Flask, request, abort, jsonify
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
from dotenv import load_dotenv
from rag_search import llm_response

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN", "")
CHANNEL_SECRET = os.getenv("CHANNEL_SECRET", "")
PORT = int(os.getenv("WEBHOOK_PORT", "5000"))

line_bot_api = LineBotApi(CHANNEL_ACCESS_TOKEN) if CHANNEL_ACCESS_TOKEN else None
handler = WebhookHandler(CHANNEL_SECRET) if CHANNEL_SECRET else None

app = Flask(__name__)

# In-Memory Storage: { user_id: [ {"role": "user/assistant", "text": "..."}, ... ] }
user_chat_history = {}
MAX_HISTORY_TURNS = 6  # Record up to 6 messages (3 conversation pairs)

def get_formatted_history(user_id):
    history_list = user_chat_history.get(user_id, [])
    if not history_list:
        return "ไม่มีประวัติการสนทนาก่อนหน้า"
    formatted = []
    for msg in history_list:
        role = "ผู้ใช้" if msg["role"] == "user" else "ระบบ"
        formatted.append(f"{role}: {msg['text']}")
    return "\n".join(formatted)

def add_to_history(user_id, role, text):
    if user_id not in user_chat_history:
        user_chat_history[user_id] = []
    user_chat_history[user_id].append({"role": role, "text": text})
    if len(user_chat_history[user_id]) > MAX_HISTORY_TURNS:
        user_chat_history[user_id] = user_chat_history[user_id][-MAX_HISTORY_TURNS:]

@app.route("/", methods=["GET"])
def index():
    return jsonify({
        "status": "online",
        "service": "SmartDoc Assistant - Coffee Barista Knowledge Graph LINE Bot",
        "endpoints": {
            "webhook": "/callback",
            "test_query": "/query?q=ขอสูตรกาแฟส้ม"
        }
    })

@app.route("/query", methods=["GET", "POST"])
def query_api():
    """HTTP API endpoint to query RAG directly without LINE for testing."""
    if request.method == "POST":
        data = request.get_json() or {}
        q = data.get("question", "")
        uid = data.get("user_id", "test_user")
    else:
        q = request.args.get("q", "")
        uid = request.args.get("user_id", "test_user")

    if not q:
        return jsonify({"error": "Missing question 'q'"}), 400

    history_context = get_formatted_history(uid)
    answer = llm_response(q, chat_history=history_context)
    add_to_history(uid, "user", q)
    add_to_history(uid, "assistant", answer)

    return jsonify({
        "question": q,
        "answer": answer,
        "history": user_chat_history.get(uid, [])
    })

@app.route("/callback", methods=["POST"])
def callback():
    if not handler:
        return "LINE Credentials not configured", 500

    signature = request.headers.get("X-Line-Signature")
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return "OK"

if handler:
    @handler.add(MessageEvent, message=TextMessage)
    def handle_message(event):
        user_id = event.source.user_id
        user_question = event.message.text.strip()
        print(f"[{user_id}] Question: {user_question}")

        # Command to reset chat history
        if user_question in ["ล้างประวัติ", "รีเซ็ต", "clear"]:
            user_chat_history.pop(user_id, None)
            line_bot_api.reply_message(
                event.reply_token,
                TextSendMessage(text="ล้างประวัติการสนทนาเรียบร้อยแล้วครับ พร้อมเริ่มถามคำถามใหม่ได้เลยครับ ☕")
            )
            return

        # 1. Fetch chat history
        history_context = get_formatted_history(user_id)

        # 2. Query Hybrid GraphRAG
        try:
            answer = llm_response(user_question, chat_history=history_context)
        except Exception as e:
            print(f"RAG Error: {e}")
            answer = "ขออภัยครับ ไม่สามารถประมวลผลคำถามได้ในขณะนี้ กรุณาลองใหม่อีกครั้งครับ"

        # 3. Store history
        add_to_history(user_id, "user", user_question)
        add_to_history(user_id, "assistant", answer)

        # 4. Reply to LINE
        line_bot_api.reply_message(
            event.reply_token,
            TextSendMessage(text=answer)
        )

if __name__ == "__main__":
    print("=" * 65)
    print(f"🚀 Starting SmartDoc Assistant Webhook Server on port {PORT}...")
    print("=" * 65)
    app.run(host="0.0.0.0", port=PORT, debug=False)
