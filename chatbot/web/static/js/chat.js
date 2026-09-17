/**
 * Chongpenyang Barista AI - Web Simulator & RAG Inspector Client
 */

const SESSION_ID = "web_sim_" + Math.random().toString(36).substring(2, 9);

document.addEventListener("DOMContentLoaded", () => {
    // Initial welcome greeting
    sendInitialGreeting();
    fetchQuickReplies();
});

function sendInitialGreeting() {
    sendMessage("สวัสดีครับ");
}

async function fetchQuickReplies() {
    try {
        const res = await fetch("/api/quick_replies");
        const data = await res.json();
        renderQuickReplies(data.quick_replies || []);
    } catch (e) {
        console.warn("Could not fetch quick replies:", e);
    }
}

function renderQuickReplies(items) {
    const bar = document.getElementById("quickRepliesBar");
    bar.innerHTML = "";
    items.forEach(item => {
        const btn = document.createElement("button");
        btn.className = "quick-chip";
        btn.textContent = item.label;
        btn.onclick = () => sendMessage(item.text);
        bar.appendChild(btn);
    });
}

function handleFormSubmit(e) {
    e.preventDefault();
    const input = document.getElementById("userInput");
    const text = input.value.trim();
    if (!text) return;
    
    input.value = "";
    sendMessage(text);
}

function sendPreset(promptText) {
    sendMessage(promptText);
}

function clearChat() {
    const chatContainer = document.getElementById("chatMessages");
    chatContainer.innerHTML = "";
    sendInitialGreeting();
}

async function triggerCarousel() {
    appendUserMessage("🍹 แสดงเมนูเครื่องดื่มยอดนิยม (Carousel)");
    scrollToBottom();
    try {
        const res = await fetch("/api/flex/carousel");
        const data = await res.json();
        appendFlexCarousel(data.carousel);
    } catch (e) {
        appendBotTextMessage("ไม่สามารถโหลด Carousel ได้: " + e);
    }
}

async function triggerTroubleshoot() {
    appendUserMessage("🔬 วินิจฉัยการสกัด Under/Over Extraction (Flex)");
    scrollToBottom();
    try {
        const res = await fetch("/api/flex/troubleshoot");
        const data = await res.json();
        appendFlexTroubleshoot(data.flex);
    } catch (e) {
        appendBotTextMessage("ไม่สามารถโหลด Flex Card ได้: " + e);
    }
}

async function sendMessage(text) {
    const chatContainer = document.getElementById("chatMessages");

    // Append User Bubble
    appendUserMessage(text);
    scrollToBottom();

    // Typing Indicator
    const typingIndicator = showTypingIndicator();
    scrollToBottom();

    const startTime = performance.now();

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text, session_id: SESSION_ID })
        });

        const data = await res.json();
        typingIndicator.remove();

        const latencyMs = Math.round(performance.now() - startTime);

        if (data.error) {
            appendBotTextMessage("⚠️ เกิดข้อผิดพลาด: " + data.error);
            return;
        }

        // Update RAG Diagnostics Sidebar
        updateRAGTelemetry(data.telemetry, latencyMs);

        // Append Bot Reply
        appendBotTextMessage(data.reply_text, data.citations);

        scrollToBottom();
    } catch (err) {
        typingIndicator.remove();
        appendBotTextMessage("❌ ไม่สามารถเชื่อมต่อกับ RAG Server ได้: " + err);
        scrollToBottom();
    }
}

function appendUserMessage(text) {
    const chatContainer = document.getElementById("chatMessages");
    const row = document.createElement("div");
    row.className = "message-row message-user";
    row.innerHTML = `<div class="bubble">${escapeHtml(text)}</div>`;
    chatContainer.appendChild(row);
}

function appendBotTextMessage(text, citations = []) {
    const chatContainer = document.getElementById("chatMessages");
    const row = document.createElement("div");
    row.className = "message-row message-bot";

    let formatted = formatMarkdownText(text);

    let citationsHtml = "";
    if (citations && citations.length > 0) {
        const chips = citations.map(c => 
            `<span class="citation-chip" title="${escapeHtml(c.preview || '')}">📄 หน้า ${c.page} - ${escapeHtml(c.topic || '')}</span>`
        ).join("");
        citationsHtml = `<div class="bubble-citations"><strong>📚 อ้างอิงคู่มือ:</strong><br>${chips}</div>`;
    }

    row.innerHTML = `
        <div class="bot-avatar">☕</div>
        <div class="bubble">
            ${formatted}
            ${citationsHtml}
        </div>
    `;
    chatContainer.appendChild(row);
}

function appendFlexCarousel(carousel) {
    const chatContainer = document.getElementById("chatMessages");
    const row = document.createElement("div");
    row.className = "message-row message-bot";

    const bubbles = carousel.contents || [];
    let itemsHtml = bubbles.map(b => {
        const h = b.header.contents;
        const title = h[1]?.text || "กาแฟ";
        const tag = h[0]?.contents?.[0]?.text || "สูตร";
        const desc = b.body?.contents?.[0]?.text || "";
        const btnText = b.footer?.contents?.[0]?.action?.text || "";

        return `
            <div style="min-width: 220px; max-width: 240px; background: #FFFFFF; border-radius: 12px; border: 1px solid #D4A373; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1); flex-shrink: 0;">
                <div style="background: #2C1810; padding: 10px 14px; color: #FFFFFF;">
                    <span style="font-size: 0.68rem; color: #D4A373; font-weight: bold;">${tag}</span>
                    <h4 style="margin-top: 2px; font-size: 0.95rem;">${title}</h4>
                </div>
                <div style="padding: 12px; font-size: 0.8rem; color: #555555;">
                    ${desc}
                </div>
                <div style="padding: 8px 12px; background: #FAF8F5; border-top: 1px solid #EEE;">
                    <button class="btn-icon" style="width: 100%;" onclick="sendMessage('${btnText}')">📖 ดูสูตรละเอียด</button>
                </div>
            </div>
        `;
    }).join("");

    row.innerHTML = `
        <div class="bot-avatar">☕</div>
        <div style="display: flex; gap: 12px; overflow-x: auto; padding: 8px 0; max-width: 100%;">
            ${itemsHtml}
        </div>
    `;
    chatContainer.appendChild(row);
    scrollToBottom();
}

function appendFlexTroubleshoot(flex) {
    const chatContainer = document.getElementById("chatMessages");
    const row = document.createElement("div");
    row.className = "message-row message-bot";

    row.innerHTML = `
        <div class="bot-avatar">🔬</div>
        <div class="flex-card-container">
            <div class="flex-card-header">
                <div style="font-size: 0.72rem; color: #D4A373; font-weight: bold;">ESPRESSO EXTRACTION DIAGNOSIS</div>
                <h3 style="font-size: 1.05rem; margin-top: 4px;">คู่มือวินิจฉัยและแก้ไขรสชาติกาแฟ</h3>
            </div>
            <div class="flex-card-body">
                <div style="background: #FFF5F5; border: 1px solid #FEB2B2; border-radius: 8px; padding: 10px; margin-bottom: 8px;">
                    <strong style="color: #C53030; font-size: 0.85rem;">⚠️ Under-Extraction (สกัดน้อยเกินไป)</strong>
                    <p style="font-size: 0.78rem; color: #4A5568; margin-top: 4px;">รสเปรี้ยวโดด ไหลเร็ว (< 20 วิ) -> <em>แก้ไขโดยบดให้ละเอียดขึ้น หรือเพิ่มปริมาณกาแฟ</em></p>
                </div>
                <div style="background: #FFFAF0; border: 1px solid #FBD38D; border-radius: 8px; padding: 10px; margin-bottom: 8px;">
                    <strong style="color: #C05621; font-size: 0.85rem;">⚠️ Over-Extraction (สกัดมากเกินไป)</strong>
                    <p style="font-size: 0.78rem; color: #4A5568; margin-top: 4px;">รสขมไหม้ ไหลช้ามาก (> 32 วิ) -> <em>แก้ไขโดยบดให้หยาบขึ้น หรือลดแรงแทมป์</em></p>
                </div>
                <div style="background: #F0FFF4; border: 1px solid #9AE6B4; border-radius: 8px; padding: 10px;">
                    <strong style="color: #276749; font-size: 0.85rem;">✅ Perfect Shot (สกัดสมบูรณ์)</strong>
                    <p style="font-size: 0.78rem; color: #2F855A; margin-top: 4px;">90-96°C | 9-10 บาร์ | 20-30 วินาที -> รสหวานฉ่ำ กลมกล่อม ครีม่าสีทอง</p>
                </div>
            </div>
            <div class="flex-card-footer">
                <button class="btn-icon" style="width: 100%;" onclick="sendMessage('วิธีปรับเบอร์บดเครื่องบดกาแฟให้เหมาะสม')">⚙️ วิธีปรับตั้งเบอร์บด</button>
            </div>
        </div>
    `;
    chatContainer.appendChild(row);
    scrollToBottom();
}

function updateRAGTelemetry(telemetry, clientLatency) {
    if (!telemetry) return;

    if (telemetry.model) document.getElementById("metricModel").textContent = telemetry.model;
    if (telemetry.retrieval) document.getElementById("metricRetrieval").textContent = telemetry.retrieval;
    if (telemetry.reranker) document.getElementById("metricReranker").textContent = telemetry.reranker;
    if (telemetry.dynamic_k) document.getElementById("metricTopK").textContent = `k = ${telemetry.dynamic_k}`;
    
    const latency = telemetry.latency_ms || clientLatency || 0;
    document.getElementById("metricLatency").textContent = `${latency} ms`;

    // Confidence Bar
    const conf = Math.min(100, Math.round((telemetry.confidence || 0.88) * 100));
    document.getElementById("metricConfidence").textContent = `${conf}%`;
    document.getElementById("confidenceBar").style.width = `${conf}%`;

    // Chunks container
    const chunksContainer = document.getElementById("chunksContainer");
    if (telemetry.chunks && telemetry.chunks.length > 0) {
        chunksContainer.innerHTML = telemetry.chunks.map((c, i) => `
            <div class="chunk-card" title="คลิกเพื่อส่งคำถามที่เกี่ยวข้อง" onclick="sendMessage('ขอข้อมูลเพิ่มเติมเรื่อง ${escapeHtml(c.topic)}')">
                <div class="chunk-header">
                    <span class="chunk-page">📄 หน้า ${c.page}</span>
                    <span class="chunk-score">Score: ${(c.score || 0).toFixed(3)}</span>
                </div>
                <div style="font-weight: 600; color: #2C1810; margin-bottom: 2px;">${escapeHtml(c.topic)}</div>
                <div class="chunk-snippet">${escapeHtml(c.content)}</div>
            </div>
        `).join("");
    }
}

function showTypingIndicator() {
    const chatContainer = document.getElementById("chatMessages");
    const row = document.createElement("div");
    row.className = "message-row message-bot typing-indicator-row";
    row.innerHTML = `
        <div class="bot-avatar">☕</div>
        <div class="bubble" style="display: flex; gap: 4px; align-items: center; padding: 12px 18px;">
            <span style="font-size: 0.82rem; color: #888;">กำลังค้นหาบริบทคู่มือและสกัดคำตอบ...</span>
        </div>
    `;
    chatContainer.appendChild(row);
    return row;
}

function scrollToBottom() {
    const container = document.getElementById("chatMessages");
    container.scrollTop = container.scrollHeight;
}

function formatMarkdownText(text) {
    if (!text) return "";
    let clean = escapeHtml(text);
    // Bold
    clean = clean.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Bullet points
    clean = clean.replace(/^• (.*?)$/gm, '<li>$1</li>');
    clean = clean.replace(/^- (.*?)$/gm, '<li>$1</li>');
    // Newlines to br
    clean = clean.replace(/\n\n/g, '</p><p>');
    clean = clean.replace(/\n/g, '<br>');
    return `<p>${clean}</p>`;
}

function escapeHtml(str) {
    if (!str) return "";
    return String(str)
        .replace(/&/g, "&amp;")
        .replace(/</g, "&lt;")
        .replace(/>/g, "&gt;")
        .replace(/"/g, "&quot;")
        .replace(/'/g, "&#039;");
}
