# ☕ SmartDoc Assistant – Production-Grade Hybrid RAG & LINE Webhook Guide

คู่มือการติดตั้ง ใช้งาน และเชื่อมต่อระบบ **SmartDoc Barista Hybrid RAG Chatbot** ร่วมกับ **LINE Messaging API** และ **Cloudflare Tunnel** 

---

## 🌟 1. สถาปัตยกรรมระบบ (System Architecture)

ระบบ RAG ถูกออกแบบตามหลัก **Production-Grade Modular OOP Architecture** แบ่งเป็นชั้นการทำงานที่ชัดเจน:

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
        │  (Dense Vector Store) │                     │  (Thai newmm Tokens)  │
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
                            └──────────────┬───────────────┘
                                           │
                                           ▼ [generation/rag_chain.py]
                            ┌──────────────────────────────┐
                            │   Ollama (qwen2.5:3b)        │
                            │   Few-Shot & CoT Reasoning   │
                            └──────────────┬───────────────┘
                                           │
                                           ▼ [generation/citation_engine.py]
                            ┌──────────────────────────────┐
                            │  Source Citations (Page/Topic)
                            └──────────────┬───────────────┘
                                           │
                                           ▼ [interfaces/webhook.py]
                            ┌──────────────────────────────┐
                            │   Flask Webhook (Port 5000)  │
                            └──────────────┬───────────────┘
                                           │
                                           ▼ [cloudflared tunnel]
                            ┌──────────────────────────────┐
                            │   Cloudflare HTTPS Tunnel    │
                            └──────────────┬───────────────┘
                                           │
                                           ▼
                            ┌──────────────────────────────┐
                            │      LINE Messaging App      │
                            └──────────────────────────────┘
```

---

## 🚀 2. ขั้นตอนการรันระบบ LINE Bot (Step-by-Step Operations)

เพื่อให้ LINE Chatbot สามารถรับข้อความจากผู้ใช้และตอบกลับได้ จะต้องเปิด **2 Terminal (PowerShell)** รันควบคู่กัน:

### 🖥️ Terminal ที่ 1: รัน Webhook Server (Flask)
เปิด PowerShell หน้าต่างที่ 1 ในโฟลเดอร์โปรเจกต์:

```powershell
# 1. เปิด Virtual Environment (ต้องมี (venv) ด้านหน้า)
.\venv\Scripts\Activate.ps1

# 2. รัน Webhook Server
python -m chatbot.interfaces.webhook
```

เมื่อระบบโหลดเสร็จสมบูรณ์ จะแสดงข้อความ:
```text
🚀 Initializing Webhook RAG Engine...
✅ BM25 indexed 339 documents.
✅ Cross-Encoder Re-ranker ready.
✅ Webhook RAG Engine initialized successfully.
🌐 Starting Server on port 5000...
 * Running on all addresses (0.0.0.0)
 * Running on http://127.0.0.1:5000
```
*(เซิร์ฟเวอร์จะเปิดรับคำสั่งอยู่ที่พอร์ต `5000`)*

---

### 🌐 Terminal ที่ 2: รัน Cloudflare Tunnel (สร้าง Public HTTPS URL)
เปิด PowerShell หน้าต่างที่ 2 (โดยไม่ต้องปิดหน้าต่างที่ 1):

```powershell
cloudflared tunnel --url http://localhost:5000
```

หน้าจอจะแสดง URL ชั่วคราวที่เป็น HTTPS ขึ้นมาในกรอบ เช่น:
```text
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
|  https://example-subdomain-here.trycloudflare.com                                          |
+--------------------------------------------------------------------------------------------+
```

> ⚠️ **ข้อควรระวังในการรัน Cloudflare Tunnel**:
> - หน้าต่าง Terminal ที่ 2 ต้องเปิดทิ้งไว้ตลอดเวลาขณะใช้งาน หากปิดหน้าต่าง Tunnel จะหยุดทำงานทันที
> - หาก Tunnel มีการหลุด ให้กด `Ctrl + C` แล้วพิมพ์ `cloudflared tunnel --url http://localhost:5000` เพื่อรับ URL ใหม่อีกครั้ง

---

### 📲 ขั้นตอนที่ 3: นำ URL ไปตั้งค่าใน LINE Developers Console

1. นำ URL ที่ได้จาก Terminal ที่ 2 มาต่อท้ายด้วย `/callback` เช่น:
   ```text
   https://example-subdomain-here.trycloudflare.com/callback
   ```
2. เข้าสู่ [LINE Developers Console](https://developers.line.biz/) $\rightarrow$ เลือก Channel ของบอทคุณ
3. ไปที่แท็บ **Messaging API**
4. ในส่วน **Webhook settings**:
   - นำ URL ไปวางลงในช่อง **Webhook URL** แล้วกดปุ่ม **Update**
   - กดปุ่ม **Verify** $\rightarrow$ ระบบต้องแสดงข้อความสีเขียวว่า **Success**
   - เลื่อนสวิตช์เปิด **Use webhook** ให้เป็น **ON (สีเขียว)**
5. ไปที่ [LINE Official Account Manager](https://manager.line.biz/):
   - ไปที่เมนู **ตั้งค่าการตอบกลับ (Response settings)**
   - ปิด **ข้อความตอบกลับอัตโนมัติ (Auto-response messages)** ให้เป็น **OFF** เพื่อไม่ให้ระบบข้อความตอบรับเดิมของ LINE ตอบซ้อนกับบอท AI
6. เปิดแอป LINE บนมือถือ แล้วเริ่มแชททดสอบกับบอทได้ทันที! ☕

---

## 🧪 3. เครื่องมือและแนวทางการทดสอบระบบ (Testing Toolkit)

### 1) ทดสอบผ่าน REST API โดยไม่ต้องผ่าน LINE
ระหว่างที่ Webhook Server กำลังรันอยู่ สามารถเปิด Browser หรือ Postman ยิงทดสอบได้ที่:
- **Health Check**: `http://localhost:5000/`
- **Query Endpoint**: `http://localhost:5000/query?q=ขอสูตรกาแฟส้ม`

### 2) ทดสอบผ่าน Interactive CLI Testbench (บน Terminal โดยตรง)
```powershell
python -m chatbot.interfaces.app_chat
```

### 3) ชุดข้อความทดสอบมาตรฐานในไฟล์ Excel
เราได้จัดทำไฟล์ Excel รวบรวม 20 คำถามทดสอบที่ครอบคลุมทุกแง่มุม (สูตรเครื่องดื่ม, การปรับเบอร์บด, การแก้ปัญหา Under/Over Extraction, การคั่ว, และการทดสอบ Guardrail ป้องกันการมโน) ไว้ที่:
👉 **[test_line_queries.xlsx](file:///d:/PIK/y4-1/241-351_AI_for_social/chongpenyang/test_line_queries.xlsx)**

---

## 📊 4. สรุปคำถามทดสอบที่แนะนำสำหรับบาริสต้า (Sample Test Queries)

| หมวดหมู่ | ตัวอย่างข้อความสำหรับพิมพ์ใน LINE | วัตถุประสงค์ที่ทดสอบ |
| :--- | :--- | :--- |
| **ขอสูตรมาตรฐาน** | `ขอสูตรและขั้นตอนการทำเอสเพรสโซ่ร้อน` | ตรวจสอบปริมาณผงกาแฟ อุณหภูมิ และเวลาสกัด |
| **สูตรเมนูเย็น** | `ขอสูตรกาแฟส้ม (Iced Orange Espresso)` | ตรวจสอบส่วนผสมน้ำส้ม น้ำแข็ง และการแยกชั้น |
| **เมนูพิเศษ** | `สูตรการทำ Dirty Coffee มีขั้นตอนอย่างไร` | ตรวจสอบเทคนิคการใช้นมเย็นจัดและการสกัดช็อต |
| **เปรียบเทียบเมนู** | `ลาเต้ร้อน กับ คาปูชิโน่ร้อน ต่างกันอย่างไร` | ตรวจสอบความเข้าใจสัดส่วนฟองนม |
| **แก้ปัญหากาแฟเปรี้ยว** | `ทำไมกาแฟถึงมีรสชาติเปรี้ยวฝาด ครีม่าซีดจาง น้ำไหลเร็ว` | ตรวจสอบการวินิจฉัย Under-Extraction |
| **แก้ปัญหากาแฟขมไหม้** | `กาแฟรสขมไหม้ น้ำกาแฟหยดช้า เกิดจากอะไรและแก้ยังไง` | ตรวจสอบการวินิจฉัย Over-Extraction |
| **วิทยาศาสตร์การคั่ว** | `ระดับการคั่วอ่อนมีค่า Agtron เท่าไร และรสชาติเป็นอย่างไร` | ตรวจสอบการดึงข้อมูลจากตาราง Agtron |
| **การสตีมนม** | `อุณหภูมินมที่เหมาะสมในการสตีมคือเท่าไร และทำไมไม่เกิน 70 องศา` | ตรวจสอบความเข้าใจวิทยาศาสตร์โปรตีนนม |
| **การบำรุงรักษา** | `การ Backflush เครื่องชงกาแฟมีขั้นตอนอย่างไรและทำเพื่ออะไร` | ตรวจสอบขั้นตอน SOP และการใช้ Blind Basket |
| **ทดสอบ Guardrail** | `แนะนำวิธีทำต้มยำกุ้งน้ำข้นหน่อยครับ` | ตรวจสอบ Zero Hallucination (ต้องปฏิเสธอย่างสุภาพ) |
| **ตรวจสอบ Citation** | `บอกสูตรกาแฟร้อนทั้งหมดในคู่มือพร้อมระบุเลขหน้าอ้างอิง` | ตรวจสอบการสร้าง Footnote อ้างอิงเลขหน้า |
