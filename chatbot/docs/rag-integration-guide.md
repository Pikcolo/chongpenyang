# ☕ Chongpenyang Barista AI – Production-Grade Hybrid RAG, Web Simulator & LINE UI Guide

คู่มือฉบับสมบูรณ์สำหรับการติดตั้ง ใช้งาน และเชื่อมต่อระบบ **Chongpenyang Barista AI** (คู่มือประกอบการฝึกอบรม หลักสูตรบาริสต้ามืออาชีพ) ที่ยกระดับสู่เกณฑ์ **Grade A / Production-Grade (4.0/4.0)** พร้อม **Web Simulator & Diagnostics Inspector** และระบบ **LINE UI ครบวงจร (Rich Menu, Contextual Quick Replies, Flex Carousel, Troubleshoot Flex)**

---

## 🌟 1. สถาปัตยกรรมระบบ (System Architecture)

ระบบถูกพัฒนาขึ้นแบบ **Modular OOP Architecture** พร้อมรองรับทั้ง Web Simulator Dashboard และ LINE Messaging API:

```
                            ┌──────────────────────────────┐
                            │   documents.pdf (53 Pages)   │
                            └──────────────┬───────────────┘
                                           │
                                           ▼ [ingestion/pdf_parser.py]
                            ┌──────────────────────────────┐
                            │  Table & Layout Extraction   │
                            └──────────────┬───────────────┘
                                           │
                                           ▼ [ingestion/chunker.py]
                            ┌──────────────────────────────┐
                            │  Parent-Child Semantic Chunks│
                            └──────────────┬───────────────┘
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    │                                             │
                    ▼ [retrieval/vector_store.py]                 ▼ [retrieval/bm25_retriever.py]
        ┌───────────────────────┐                     ┌───────────────────────┐
        │  ChromaDB / FAISS     │                     │  BM25 Sparse Search   │
        │  (Dense Vector Store) │                     │  (PyThaiNLP Tokens)   │
        └───────────┬───────────┘                     └───────────┬───────────┘
                    │                                             │
                    └──────────────────────┬──────────────────────┘
                                           │
                                           ▼ [retrieval/fusion.py]
                            ┌──────────────────────────────┐
                            │ Reciprocal Rank Fusion (RRF) │
                            └──────────────┬───────────────┘
                                           │
                                           ▼ [retrieval/reranker.py]
                            ┌──────────────────────────────┐
                            │  Cross-Encoder Re-ranker     │
                            │  (mmarco-mMiniLMv2-L12-H384) │
                            └──────────────┬───────────────┘
                                           │
                                           ▼ [generation/guardrails.py]
                            ┌──────────────────────────────┐
                            │  Zero-Hallucination Guardrail│
                            │  & Barista Term Sanitization │
                            └──────────────┬───────────────┘
                                           │
                                           ▼ [generation/rag_chain.py]
                            ┌──────────────────────────────┐
                            │   Ollama LLM (qwen2.5:3b)    │
                            │   Few-Shot & CoT Reasoning   │
                            └──────────────┬───────────────┘
                                           │
                                           ▼ [generation/citation_engine.py]
                            ┌──────────────────────────────┐
                            │  📌 Official Citations Footer│
                            └──────────────┬───────────────┘
                                           │
                    ┌──────────────────────┴──────────────────────┐
                    │                                             │
                    ▼                                             ▼
        ┌───────────────────────┐                     ┌───────────────────────┐
        │  Web Simulator & UI   │                     │ LINE Messaging API    │
        │  (Port 5000 /)        │                     │ (Port 5000 /callback) │
        │  • Realtime Inspector │                     │ • 6-Grid Rich Menu    │
        │  • Thinking UI Anim   │                     │ • Native Loading Anim │
        │  • Assistant Cards    │                     │ • Contextual QRs      │
        │  • 1-Click Test Qs    │                     │ • Flex Carousels      │
        └───────────────────────┘                     └───────────────────────┘
```

---

## 🎨 2. จุดเด่นของหน้าตาและระบบ UI (User Interface Features)

### 2.1 Web Testing Simulator & Realtime Diagnostics Inspector (`http://localhost:5000`)
- **ฝั่งซ้าย (Inspector Sidebar):**
  - **RAG Telemetry เรียลไทม์:** แสดงโมเดลที่ใช้งาน (`qwen2.5:3b` หรือ `llama3.2:3b`), เอนจินสืบค้น (`FAISS Dense + BM25 PyThaiNLP + RRF`), Re-ranker (`Cross-Encoder`), Dynamic $k$, Re-rank Confidence Progress Bar, และค่า Latency (ms)
  - **Retrieved Chunks Viewer:** แสดงบล็อกข้อความจริงที่ดึงมาจาก PDF พร้อมคะแนนความเหมือน และเลขหน้าเอกสารต้นทาง
  - **1-Click Test Prompts:** ปุ่มกดทดสอบคำถาม 6 หมวดสำคัญตามเกณฑ์ Rubric Score
- **ฝั่งขวา (Chat Simulator):**
  - **Animated Thinking UI:** แสดงการ์ดสถานะกำลังค้นคว้าแบบเคลื่อนไหว (จุดเด้ง ● ● ●, แถบ Shimmer, และสเต็ปการทำงานเรียลไทม์) ขณะรอ LLM
  - **Assistant Card Layout:** กล่องข้อความตอบกลับแถบหัวข้อเขียวมรกต พร้อมชื่อเรื่อง `❓ {คำถาม}`, เนื้อหาแยกข้อย่อยชัดเจน, และส่วนอ้างอิง `📌 อ้างอิงคู่มือบาริสต้ามืออาชีพ:` ท้ายการ์ด
  - **Dynamic Quick Reply Chips:** แถบปุ่มลัดด้านล่างที่ปรับเปลี่ยนตามหัวข้อที่เพิ่งสนทนา

### 2.2 ระบบ LINE UI เต็มรูปแบบ (ตามสไตล์ Barista Assistant)
- **Official LINE Rich Menu (ขนาดมาตรฐาน 2500x1686 - Barista Custom Artwork):**
  - ดีไซน์การ์ดเมนู 6 ช่องธีมกาแฟพรีเมียม (Coffee Tone UI) พร้อมคำสั่งลัด:
    1. ☕ **สูตร Perfect Shot** (9-10 บาร์ & 90-95°C)
    2. 🥛 **สตีมนม & ลาเต้อาร์ต** (Microfoam 60-65°C)
    3. ⚙️ **การปรับเบอร์บด** (Calibration & Flow rate)
    4. 🍹 **เมนูเครื่องดื่ม** (Americano, Latte, กาแฟส้ม ฯลฯ)
    5. 🔬 **วิเคราะห์รสชาติ** (Under/Over Extraction)
    6. 📖 **สารบัญคู่มือ** (5 โมดูลหลักสูตรบาริสต้ามืออาชีพ)
  - ตั้งค่า `"selected": True` ให้แสดง Rich Menu อัตโนมัติเมื่อเข้าห้องแชท พร้อมระบบพับเก็บเปิดแป้นพิมพ์ได้ตลอดเวลา
  - ระบบประมวลผลภาพอัตโนมัติ: ดึงภาพต้นฉบับ `rich_menu_barista.png` มา Resize สเกลเป็น 2500x1686 และบีบอัดคุณภาพสูง (< 1 MB) เป็น `rich_menu_line.jpg` สำหรับส่งขึ้น LINE CDN ทันที
- **Contextual Quick Reply Chips (ขับเคลื่อนด้วย Taxonomy จาก Knowledge Graph):**
  - ตรวจจับบริบทแล้วสลับปุ่มให้ผู้ใช้กดถามต่อได้ทันทีสูงสุด 12 ปุ่ม ครอบคลุมทั้ง 5 โมดูล (MOD_01 ถึง MOD_05)
  - กำกับความยาวข้อความปุ่มทุกปุ่มให้ไม่เกิน 20 ตัวอักษรอย่างเข้มงวดตามข้อกำหนดของ LINE Messaging API
- **Stunning Flex Message Carousel (8 เมนูเครื่องดื่มมาตรฐานจากคู่มือ):**
  - การ์ดสไลด์แนวนอนขนาด Mega พร้อม Color Palette เฉพาะเมนู, ป้าย Badge, ตารางพารามิเตอร์ (สัดส่วน, เวลา/อุณหภูมิ, มาตรฐาน), กล่องเคล็ดลับบาริสต้า (Barista Tips) และปุ่ม Dual Actions:
    1. `📖 ดูวิธีทำ SOP ละเอียด`
    2. `⚙️ พารามิเตอร์การสกัด`
  - ครอบคลุมทั้ง 8 เมนูหลัก: เอสเพรสโซ่ เพอร์เฟกต์ช็อต, อเมริกาโน่เย็น, คาเฟ่ ลาเต้ & อาร์ต, คาปูชิโน่ร้อน, เอสเพรสโซ่เย็นสไตล์ไทย, กาแฟส้ม, กาแฟพีช, กาแฟน้ำผึ้งมะนาว
- **Extraction Troubleshoot Flex Card:**
  - การ์ดเปรียบเทียบข้อผิดพลาดการสกัด 3 สถานะ: Under-Extraction (สีแดง) vs Over-Extraction (สีส้ม) vs Perfect Shot (สีเขียว) พร้อมคำแนะนำการแก้ไขทันที
- **Safe Reply Fallback Engine:**
  - เพิ่มระบบตรวจจับข้อผิดพลาดและ Fallback ส่ง Plain Text หาก API ของ LINE มีการเปลี่ยนแปลงหรือเกิดข้อผิดพลาด ป้องกันปัญหา 500 error

### 2.3 โครงสร้างหลักสูตร 5 โมดูลอย่างเป็นทางการ (Official 5 Curriculum Modules)

ระบบจัดโครงสร้าง Taxonomy และ Metadata ตามคู่มือฝึกอบรมบาริสต้ามืออาชีพ (53 หน้า) ออกเป็น 5 โมดูลหลัก:

| โมดูล | ชื่อโมดูล | ช่วงหน้า | ขอบเขตเนื้อหาสำคัญ |
|:---:|---|:---:|---|
| **MOD_01** | ความรู้เบื้องต้นเกี่ยวกับเมล็ดกาแฟ | หน้า 3 – 19 | • ประวัติความเป็นมาและแหล่งกำเนิดกาแฟโลก (ตำนาน Kaldi)<br>• สายพันธุ์กาแฟหลัก (Arabica, Robusta, Peaberry)<br>• สายพันธุ์ย่อยยอดนิยม (Typica, Bourbon, Caturra, Catuai, Geisha)<br>• ปัจจัยการเพาะปลูก: ระดับความสูง, อุณหภูมิ, ปริมาณน้ำฝน<br>• 10 ขั้นตอนการผลิตจากต้นสู่แก้ว (ปลูก, เก็บเกี่ยว, แปรรูป Washed/Dry/Honey, สีเมล็ด, คัดเกรด, Cupping, คั่ว, บด, ชง, เสิร์ฟ)<br>• ระดับการคั่ว (Light, Medium, Dark/French) และตารางสเกล Agtron (80-70 ถึง 30-25)<br>• เบอร์บดกาแฟ 5 ระดับ (Extra Fine ถึง Coarse) และการเลือกใช้อุปกรณ์ชง |
| **MOD_02** | เคล็ดลับการชงกาแฟ หลักการและวิธีการ | หน้า 20 – 31 | • วิทยาศาสตร์การสกัดกาแฟ (Extraction Parameters)<br>• คุณภาพน้ำ, อุณหภูมิน้ำในการสกัด (90–96°C), แรงดัน (9-10 บาร์)<br>• การประเมินสถานะการสกัด: **Espresso Perfect Shot** (20-30s, 1-1.5 oz), **Under Extraction** (สกัดน้อยเกินไป), **Over Extraction** (สกัดมากเกินไป)<br>• อาการของครีม่า (Crema), รสชาติ (Sensory Profile), สาเหตุ และแนวทางแก้ไข<br>• ปรากฏการณ์ **Channeling** สาเหตุและวิธีป้องกัน (WDT, ระนาบการแทมป์ 90°)<br>• การบำรุงรักษา: ด้ามชง Bottomless Naked Portafilter และการทำ Backflush |
| **MOD_03** | ประวัติความเป็นมาและศาสตร์ของลาเต้อาร์ต | หน้า 32 – 36 | • ประวัติและต้นกำเนิด Latte Art (David Schomer / Espresso Vivace, Seattle, Luigi Bezzera 1901)<br>• การแข่งขัน World Latte Art Championship (WLAC) และแชมป์โลก (Manuela Fensore 2019)<br>• วิทยาศาสตร์ฟองนม (Microfoam): โปรตีนเคซีนและไขมันนมที่อุณหภูมิ 60–65°C (ไม่เกิน 70°C)<br>• เทคนิคการเท 2 รูปแบบ: Free Pour (ลาย Heart, Tulip, Rosetta) และ Etching (การวาดลาย) |
| **MOD_04** | ใบขั้นตอนการปฏิบัติงาน การชงกาแฟร้อนและเย็น (SOP) | หน้า 37 – 50 | • สูตรและสัดส่วนมาตรฐานของเมนูกาแฟ 13 เมนู (ร้อน 5 เมนู, เย็น 8 เมนู)<br>• อัตราส่วนวัตถุดิบ (Dose, Yield, สัดส่วนนม/น้ำเชื่อม/น้ำผลไม้)<br>• อุปกรณ์เฉพาะทางและเครื่องบด/เครื่องชงประจำเมนู<br>• ขั้นตอน Standard Operating Procedure (SOP) ทีละสเต็ป<br>• เทคนิคและ Barista Tips ประจำแต่ละเมนู (Espresso, Americano, Latte, Cappuccino, Thai Iced Espresso, กาแฟส้ม, กาแฟพีช, กาแฟน้ำผึ้งมะนาว, ลาเต้มิ้นท์) |
| **MOD_05** | ใบงาน ใบทดสอบ และใบเฉลย | หน้า 51 – 53 | • แบบทดสอบวัดระดับความรู้บาริสต้า (การประเมินช็อต, พารามิเตอร์, อุณหภูมิ)<br>• Checklist ตรวจสอบทักษะการชงและการจัดการบาร์<br>• แนวทางปฏิบัติและเฉลยคำตอบมาตรฐานตามเกณฑ์บาริสต้ามืออาชีพ |

เอกสารรายงานการประเมินทางเทคนิคเพิ่มเติม:
- 🔬 [คู่มือเปรียบเทียบโมเดล Embedding (BGE-M3 vs E5-base vs MiniLM)](file:///d:/PIK/y4-1/241-351_AI_for_social/chongpenyang/chatbot/docs/embedding-models-comparison.md)
- 🧠 [คู่มือเปรียบเทียบโมเดล LLM กะทัดรัด (Qwen 2.5 3B vs Gemma 2 2B vs Llama 3.2 3B)](file:///d:/PIK/y4-1/241-351_AI_for_social/chongpenyang/chatbot/docs/llm-selection-and-comparison.md)

---

## 🚀 3. ขั้นตอนการรันระบบ (Step-by-Step Operations)

### ขั้นตอนที่ 1: เปิดใช้งาน LINE Rich Menu (ทำเพียงครั้งแรก หรือเมื่ออัปเดตรูป)
```powershell
.\venv\Scripts\Activate.ps1
python setup_rich_menu.py
```
*ระบบจะนำภาพต้นฉบับมาแปลงขนาดเป็น 2500x1686 (< 1MB), ลงทะเบียน Rich Menu Schema กับ LINE API, อัปโหลดภาพเข้า CDN, ตั้งเป็น Default Rich Menu ทันที และล้าง Rich Menu เก่าออกอัตโนมัติ*

---

### ขั้นตอนที่ 2: รัน Unified Server (Web Simulator + Webhook)
เปิด PowerShell หน้าต่างที่ 1:
```powershell
.\venv\Scripts\Activate.ps1
python main.py
# หรือ
python -m chatbot.interfaces.webhook
```
เมื่อโหลดเสร็จจะขึ้นข้อความ:
```text
✅ BM25 indexed 339 documents.
✅ Cross-Encoder Re-ranker ready.
✅ Production RAG Engine online and ready.
🌐 Starting Chongpenyang Barista AI Server on port 5000...
📱 Web Simulator & Inspector: http://localhost:5000
🔗 LINE Webhook URL: http://localhost:5000/callback
```
- **เปิดเบราว์เซอร์ไปที่:** `http://localhost:5000` เพื่อใช้งาน Web Simulator และ Inspector

---

### ขั้นตอนที่ 3: เปิด Cloudflare Tunnel เชื่อมต่อ LINE
เปิด PowerShell หน้าต่างที่ 2:
```powershell
cloudflared tunnel --url http://localhost:5000
```
คัดลอก HTTPS URL ที่ได้ เช่น:
```text
https://xxxx-xxxx.trycloudflare.com
```
นำไปต่อท้ายด้วย `/callback` แล้วใส่ใน **LINE Developers Console**:
```text
https://xxxx-xxxx.trycloudflare.com/callback
```
*(กด Verify ให้ขึ้นสถานะ Success และเปิดใช้งาน Use Webhook)*

---

## 🧪 4. ชุดคำถามทดสอบคุณภาพ (Verification Queries)

| ลำดับ | คำถามทดสอบ | พฤติกรรมและผลลัพธ์ที่ถูกต้อง |
|:---:|---|---|
| 1 | `สวัสดีครับ` | แนะนำตัวเป็น Chongpenyang Barista AI และไม่แสดง Citation ปลอม |
| 2 | `อุณหภูมิน้ำและแรงดันในการสกัดเอสเพรสโซ่ที่ถูกต้องคือเท่าไร?` | ตอบ 90-96°C และ 9-10 บาร์ (ไม่มีคำว่า "มิลลิแปร"), พร้อมแนบ `📌 อ้างอิงคู่มือ:` หน้า 24/30 |
| 3 | `เทคนิคการสตีมนมและทำลาเต้อาร์ต อุณหภูมิเท่าไร?` | ตอบอุณหภูมิ 60-65°C พร้อม Quick Replies แนะนำลาย Rosetta/Tulip/Heart |
| 4 | `ขอสูตรกาแฟส้ม (Black Orange Coffee)` | สรุปสัดส่วนน้ำส้ม 120ml และ Espresso 2 ช็อตตามคู่มือ SOP |
| 5 | `วิธีแก้ปัญหากาแฟรสชาติเปรี้ยวเกินไปหรือขมเกินไป` | สรุปเปรียบเทียบ Under-Extraction vs Over-Extraction และการตั้งเบอร์บด |
| 6 | `แนะนำวิธีทำเค้กช็อกโกแลตลาวาหน่อยครับ` | Trigger Zero-Hallucination Guardrail ปฏิเสธอย่างสุภาพทันที |

*(ดูชุดทดสอบแบบเต็ม 20 ข้อ พร้อมคำตอบที่คาดหวังและผลการประเมินได้ที่ [test_line_queries.json](file:///d:/PIK/y4-1/241-351_AI_for_social/chongpenyang/test_line_queries.json))*
