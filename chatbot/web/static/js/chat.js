/**
 * Chongpenyang Barista AI - Web Simulator & RAG Inspector Client
 * Features:
 * - Animated Thinking UI with live step progression
 * - Official Assistant Card layout matching User Specifications (Teal Header, Question Title, Citations)
 */

const SESSION_ID = "web_sim_" + Math.random().toString(36).substring(2, 9);
let thinkingInterval = null;

document.addEventListener("DOMContentLoaded", () => {
    // Initial welcome greeting
    sendInitialGreeting();
});

function sendInitialGreeting() {
    sendMessage("สวัสดีครับ");
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
    appendUserMessage("🍹 แนะนำสูตรเมนูเครื่องดื่มยอดนิยมตามคู่มือ");
    scrollToBottom();
    try {
        const res = await fetch("/api/flex/carousel");
        const data = await res.json();
        appendFlexCarousel(data.carousel);
    } catch (e) {
        appendBotTextMessage("ไม่สามารถโหลด Carousel ได้: " + e, [], "เมนูเครื่องดื่ม");
    }
}

async function triggerTroubleshoot() {
    appendUserMessage("🔬 วินิจฉัยการสกัด Under/Over Extraction");
    scrollToBottom();
    try {
        const res = await fetch("/api/flex/troubleshoot");
        const data = await res.json();
        appendFlexTroubleshoot(data.flex);
    } catch (e) {
        appendBotTextMessage("ไม่สามารถโหลด Flex Card ได้: " + e, [], "การวินิจฉัยสกัดกาแฟ");
    }
}

async function sendMessage(text) {
    const chatContainer = document.getElementById("chatMessages");

    // Append User Bubble
    appendUserMessage(text);
    scrollToBottom();

    // Show Animated Thinking UI Card
    const typingIndicator = showTypingIndicator(text);
    scrollToBottom();

    const startTime = performance.now();

    try {
        const res = await fetch("/api/chat", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ message: text, session_id: SESSION_ID })
        });

        const data = await res.json();
        
        // Stop thinking animation and remove card
        clearInterval(thinkingInterval);
        typingIndicator.remove();

        const latencyMs = Math.round(performance.now() - startTime);

        if (data.error) {
            appendBotTextMessage("⚠️ เกิดข้อผิดพลาด: " + data.error, [], text);
            return;
        }

        // Update RAG Diagnostics Sidebar
        updateRAGTelemetry(data.telemetry, latencyMs);

        // Append Bot Reply with Card Layout
        appendBotTextMessage(data.reply_text, data.citations, text);

        // Update Quick Replies dynamically based on conversation topic
        if (data.quick_replies && data.quick_replies.length > 0) {
            renderQuickReplies(data.quick_replies);
        }

        scrollToBottom();
    } catch (err) {
        clearInterval(thinkingInterval);
        typingIndicator.remove();
        appendBotTextMessage("❌ ไม่สามารถเชื่อมต่อกับ RAG Server ได้: " + err, [], text);
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

function appendBotTextMessage(text, citations = [], question = "") {
    const chatContainer = document.getElementById("chatMessages");
    const row = document.createElement("div");
    row.className = "message-row message-bot";

    // Split out raw citation block if present in the text string
    let mainAnswer = text;
    if (mainAnswer.includes("📌 **อ้างอิง")) {
        mainAnswer = mainAnswer.split("📌 **อ้างอิง")[0];
    }
    if (mainAnswer.includes("────────────────────")) {
        mainAnswer = mainAnswer.split("────────────────────")[0];
    }
    if (mainAnswer.includes("📚 **แหล่งอ้างอิง")) {
        mainAnswer = mainAnswer.split("📚 **แหล่งอ้างอิง")[0];
    }

    let formatted = formatMarkdownText(mainAnswer.trim());

    // Build Citations Section (matching user image layout)
    let citationsHtml = "";
    if (citations && citations.length > 0) {
        const listItems = citations.map(c => 
            `<li>• หน้า ${c.page} - ${escapeHtml(c.topic || 'เนื้อหาคู่มือ')}</li>`
        ).join("");

        citationsHtml = `
            <div class="card-citations-divider"></div>
            <div class="card-citations-header">
                <span>📌</span>
                <strong>อ้างอิงคู่มือบาริสต้ามืออาชีพ:</strong>
            </div>
            <ul class="card-citations-list">
                ${listItems}
            </ul>
        `;
    }

    // Question title clean display
    const cleanQ = question ? question.replace(/^(ขอ|ช่วย|อธิบาย)?(สูตร|เทคนิค)?/i, '').trim() : "ข้อมูลบาริสต้ามืออาชีพ";
    const displayTitle = question.length > 40 ? (question.substring(0, 38) + "...") : (question || "ข้อมูลหลักสูตรบาริสต้า");

    row.innerHTML = `
        <div class="bot-avatar">☕</div>
        <div class="assistant-card">
            <div class="assistant-card-header">
                <h3>Chongpenyang Barista Assistant</h3>
                <p>คู่มือประกอบการฝึกอบรม หลักสูตรบาริสต้ามืออาชีพ</p>
            </div>
            <div class="assistant-card-body">
                <div class="card-question-title">
                    <span class="icon-q">❓</span>
                    <span>${escapeHtml(displayTitle)}</span>
                </div>
                <div class="card-content-text">
                    ${formatted}
                </div>
                ${citationsHtml}
            </div>
        </div>
    `;
    chatContainer.appendChild(row);
}

function showTypingIndicator(question = "") {
    const chatContainer = document.getElementById("chatMessages");
    const row = document.createElement("div");
    row.className = "message-row message-bot typing-indicator-row";

    const displayTitle = question.length > 40 ? (question.substring(0, 38) + "...") : (question || "ประมวลผลคำถาม");

    row.innerHTML = `
        <div class="bot-avatar">☕</div>
        <div class="thinking-card">
            <div class="thinking-header">
                <div class="thinking-header-left">
                    <h3>Chongpenyang Barista Assistant</h3>
                    <p>คู่มือประกอบการฝึกอบรม หลักสูตรบาริสต้ามืออาชีพ</p>
                </div>
                <div class="thinking-pulse-dot" title="ระบบกำลังค้นคว้าบริบท"></div>
            </div>
            <div class="thinking-body">
                <div class="card-question-title" style="margin-bottom: 8px;">
                    <span class="icon-q">❓</span>
                    <span>${escapeHtml(displayTitle)}</span>
                </div>
                <div class="thinking-status-row">
                    <div class="thinking-dots">
                        <span></span>
                        <span></span>
                        <span></span>
                    </div>
                    <span class="thinking-status-text" id="thinkingStatusText">กำลังค้นหาข้อมูลจากคู่มือบาริสต้า...</span>
                </div>
                <div class="shimmer-line"></div>
                <div class="shimmer-line shimmer-line-short"></div>
            </div>
        </div>
    `;
    chatContainer.appendChild(row);

    // Dynamic Step Progression
    const steps = [
        "🧠 กำลังค้นหาข้อมูลจากคู่มือบาริสต้า...",
        "⚡ กำลังทำ Hybrid Search (ChromaDB + BM25)...",
        "🎯 กำลังทำ Cross-Encoder Re-ranking...",
        "☕ กำลังวิเคราะห์และเรียบเรียงคำตอบ..."
    ];
    let stepIdx = 0;
    thinkingInterval = setInterval(() => {
        stepIdx = (stepIdx + 1) % steps.length;
        const el = document.getElementById("thinkingStatusText");
        if (el) el.textContent = steps[stepIdx];
    }, 1800);

    return row;
}

function appendFlexCarousel(carousel) {
    const chatContainer = document.getElementById("chatMessages");
    const row = document.createElement("div");
    row.className = "message-row message-bot";

    const bubbles = carousel.contents || [];
    let itemsHtml = bubbles.map(b => {
        const headerContents = b.header?.contents || [];
        const tag = headerContents[0]?.contents?.[0]?.text || "☕ กาแฟ";
        const badgeColor = headerContents[0]?.contents?.[0]?.color || "#FFD54F";
        const title = headerContents[1]?.text || "สูตรกาแฟ";
        const subtitle = headerContents[2]?.text || "";
        const headerBg = b.header?.backgroundColor || "#1F130B";

        const bodyContents = b.body?.contents || [];
        const desc = bodyContents[0]?.text || "";
        
        // Specs inside bodyContents[2]
        const specsBox = bodyContents[2]?.contents || [];
        const ratio = specsBox[0]?.contents?.[1]?.text || "";
        const params = specsBox[1]?.contents?.[1]?.text || "";
        const standard = specsBox[2]?.contents?.[1]?.text || "";

        // Tip inside bodyContents[3]
        const tip = bodyContents[3]?.contents?.[0]?.text || "";

        // Footer buttons
        const footerContents = b.footer?.contents || [];
        const btn1Text = footerContents[0]?.action?.text || "";
        const btn1Label = footerContents[0]?.action?.label || "📖 ดูวิธีทำ SOP ละเอียด";
        const btn2Text = footerContents[1]?.action?.text || "";
        const btn2Label = footerContents[1]?.action?.label || "⚙️ พารามิเตอร์การสกัด";

        return `
            <div class="carousel-card-item" style="min-width: 280px; max-width: 300px; background: #FFFFFF; border-radius: 16px; border: 1px solid #E2E8F0; overflow: hidden; box-shadow: 0 6px 18px rgba(0,0,0,0.09); flex-shrink: 0; display: flex; flex-direction: column; transition: transform 0.2s, box-shadow 0.2s;">
                <!-- Header -->
                <div style="background: ${headerBg}; padding: 14px 16px; color: #FFFFFF; border-bottom: 2px solid ${badgeColor};">
                    <span style="display: inline-block; font-size: 0.65rem; color: ${badgeColor}; font-weight: 700; background: rgba(255,255,255,0.1); padding: 2px 8px; border-radius: 12px; letter-spacing: 0.5px;">${escapeHtml(tag)}</span>
                    <h4 style="margin: 6px 0 2px 0; font-size: 1.05rem; font-weight: 700; color: #FFFFFF; line-height: 1.3;">${escapeHtml(title)}</h4>
                    ${subtitle ? `<div style="font-size: 0.72rem; color: #D7CCC8;">${escapeHtml(subtitle)}</div>` : ''}
                </div>
                <!-- Body -->
                <div style="padding: 14px; font-size: 0.82rem; color: #4A5568; line-height: 1.45; flex: 1; display: flex; flex-direction: column; gap: 8px;">
                    <div style="color: #2D3748; font-size: 0.8rem; line-height: 1.4;">${escapeHtml(desc)}</div>
                    
                    <!-- Specs Grid -->
                    <div style="background: #F8FAFC; border: 1px solid #EDF2F7; border-radius: 8px; padding: 10px; font-size: 0.75rem; display: flex; flex-direction: column; gap: 4px;">
                        ${ratio ? `<div style="display: flex;"><span style="color: #718096; min-width: 70px;">☕ สัดส่วน:</span><strong style="color: #1A202C;">${escapeHtml(ratio)}</strong></div>` : ''}
                        ${params ? `<div style="display: flex;"><span style="color: #718096; min-width: 70px;">⏱️ พารามิเตอร์:</span><strong style="color: #2B6CB0;">${escapeHtml(params)}</strong></div>` : ''}
                        ${standard ? `<div style="display: flex;"><span style="color: #718096; min-width: 70px;">🎯 มาตรฐาน:</span><span style="color: #22543D;">${escapeHtml(standard)}</span></div>` : ''}
                    </div>

                    <!-- Tip -->
                    ${tip ? `
                        <div style="background: #FFFDF5; border-left: 3px solid #ECC94B; padding: 6px 8px; border-radius: 4px; font-size: 0.72rem; color: #744210; line-height: 1.35;">
                            ${escapeHtml(tip)}
                        </div>
                    ` : ''}
                </div>
                <!-- Footer Actions -->
                <div style="padding: 10px 14px; background: #FAF5EE; border-top: 1px solid #EDF2F7; display: flex; flex-direction: column; gap: 6px;">
                    <button class="btn-icon" style="width: 100%; background: #0A7E76; color: #FFF; border: none; font-size: 0.78rem; font-weight: 600; padding: 7px;" onclick="sendMessage('${escapeHtml(btn1Text)}')">${escapeHtml(btn1Label)}</button>
                    ${btn2Text ? `
                        <button class="btn-icon" style="width: 100%; background: #E2E8F0; color: #2D3748; border: none; font-size: 0.72rem; font-weight: 600; padding: 6px;" onclick="sendMessage('${escapeHtml(btn2Text)}')">${escapeHtml(btn2Label)}</button>
                    ` : ''}
                </div>
            </div>
        `;
    }).join("");

    row.innerHTML = `
        <div class="bot-avatar">🍹</div>
        <div style="max-width: 100%; overflow: hidden;">
            <div style="font-size: 0.78rem; color: #718096; margin-bottom: 6px; font-weight: 600;">
                🍹 8 เมนูเครื่องดื่มบาริสต้ามาตรฐาน (เลื่อนซ้าย-ขวาเพื่อดูทั้งหมด):
            </div>
            <div class="flex-carousel-scroll" style="display: flex; gap: 14px; overflow-x: auto; padding: 6px 2px 14px 2px; scroll-snap-type: x mandatory; -webkit-overflow-scrolling: touch;">
                ${itemsHtml}
            </div>
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
        <div class="assistant-card" style="max-width: 580px;">
            <div class="assistant-card-header">
                <h3>Chongpenyang Barista Assistant</h3>
                <p>ESPRESSO EXTRACTION DIAGNOSIS</p>
            </div>
            <div class="assistant-card-body">
                <div class="card-question-title">
                    <span class="icon-q">🔬</span>
                    <span>คู่มือวินิจฉัยและแก้ไขรสชาติกาแฟ (Under vs Over Extraction)</span>
                </div>
                <div style="background: #FFF5F5; border: 1px solid #FEB2B2; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                    <strong style="color: #C53030; font-size: 0.88rem;">⚠️ Under-Extraction (สกัดน้อยเกินไป)</strong>
                    <p style="font-size: 0.8rem; color: #4A5568; margin-top: 4px; line-height: 1.4;">• รสชาติ: เปรี้ยวโดด ฝาด จืด ไม่มีบอดี้<br>• ลักษณะ: ไหลเร็วเกินไป (< 20 วินาที) ครีม่าซีด<br>• <strong>วิธีแก้:</strong> ปรับเบอร์บดให้ละเอียดขึ้น หรือเพิ่มปริมาณผงกาแฟ</p>
                </div>
                <div style="background: #FFFAF0; border: 1px solid #FBD38D; border-radius: 8px; padding: 12px; margin-bottom: 10px;">
                    <strong style="color: #C05621; font-size: 0.88rem;">⚠️ Over-Extraction (สกัดมากเกินไป)</strong>
                    <p style="font-size: 0.8rem; color: #4A5568; margin-top: 4px; line-height: 1.4;">• รสชาติ: ขมไหม้ แห้งติดคอ<br>• ลักษณะ: น้ำกาแฟหยดช้ามาก (> 32 วินาที) ครีม่าสีเข้มจัด<br>• <strong>วิธีแก้:</strong> ปรับเบอร์บดให้หยาบขึ้น หรือลดแรงแทมป์</p>
                </div>
                <div style="background: #F0FFF4; border: 1px solid #9AE6B4; border-radius: 8px; padding: 12px;">
                    <strong style="color: #276749; font-size: 0.88rem;">✅ Perfect Shot (สกัดสมบูรณ์)</strong>
                    <p style="font-size: 0.8rem; color: #2F855A; margin-top: 4px; line-height: 1.4;">• อุณหภูมิน้ำ: 90 - 96 °C | แรงดัน: 9 - 10 บาร์<br>• เวลาสกัด: 20 - 30 วินาที | รสหวานฉ่ำ กลมกล่อม ครีม่าสีทอง</p>
                </div>
                <div style="margin-top: 14px;">
                    <button class="btn-icon" style="width: 100%; background: #0A7E76; color: #FFF; border: none; padding: 10px;" onclick="sendMessage('วิธีปรับเบอร์บดเครื่องบดกาแฟให้เหมาะสม')">⚙️ วิธีตั้งเบอร์บดเครื่องบดกาแฟ</button>
                </div>
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

function scrollToBottom() {
    const container = document.getElementById("chatMessages");
    container.scrollTop = container.scrollHeight;
}

function formatMarkdownText(text) {
    if (!text) return "";
    let clean = escapeHtml(text);
    // Bold
    clean = clean.replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>');
    // Numbered lists e.g. "1. "
    clean = clean.replace(/^(\d+)\.\s+(.*?)$/gm, '<p style="margin-bottom: 6px;"><strong>$1.</strong> $2</p>');
    // Bullet points
    clean = clean.replace(/^• (.*?)$/gm, '<li style="margin-left: 18px;">$1</li>');
    clean = clean.replace(/^- (.*?)$/gm, '<li style="margin-left: 18px;">$1</li>');
    // Newlines
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
