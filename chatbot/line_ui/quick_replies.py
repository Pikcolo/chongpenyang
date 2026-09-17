"""
Quick Reply Builder for LINE Bot.
Provides one-tap instant command triggers for seamless NLP navigation.
"""

from linebot.models import QuickReply, QuickReplyButton, MessageAction, PostbackAction

def get_barista_quick_replies() -> QuickReply:
    """Returns persistent quick reply navigation buttons for Barista Chatbot."""
    items = [
        QuickReplyButton(action=MessageAction(label="☕ เมนูร้อน", text="ขอเมนูร้อน")),
        QuickReplyButton(action=MessageAction(label="🧊 เมนูเย็น", text="ขอเมนูเย็น")),
        QuickReplyButton(action=MessageAction(label="🎲 Top 5 แนะนำ", text="ขอ 5 เมนูแนะนำ")),
        QuickReplyButton(action=MessageAction(label="⚠️ แก้กาแฟเปรี้ยว/ขม", text="กาแฟเปรี้ยวฝาดแก้ยังไง")),
        QuickReplyButton(action=MessageAction(label="📖 Perfect Shot", text="ตัวแปรมาตรฐานการสกัดเอสเพรสโซ่")),
    ]
    return QuickReply(items=items)
