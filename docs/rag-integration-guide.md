# SmartDoc Assistant – Hybrid GraphRAG & LINE Webhook Integration Guide

This guide explains how to operate the **SmartDoc Assistant** chatbot, which integrates:
1. **Neo4j Knowledge Graph** (Domain Ontology, Recipes, SOP Steps, Extraction Diagnosis, Coffee Agriculture)
2. **FAISS Vector Database & BM25** (Dense + Sparse Hybrid Retrieval over `documents.pdf`)
3. **LLM Generation** (Ollama `qwen2.5:7b` / Cloud LLMs with multi-turn conversation memory)
4. **LINE Messaging API Webhook** (Flask server for real-time mobile interaction)

---

## 1. Architecture Overview

```
                          ┌─────────────────────────────┐
                          │   documents.pdf (53 Pages)   │
                          └──────────────┬──────────────┘
                                         │
                 ┌───────────────────────┴───────────────────────┐
                 │                                               │
                 ▼                                               ▼
     ┌───────────────────────┐                       ┌───────────────────────┐
     │   feed_graph.py       │                       │    build_index.py     │
     │  (Domain Extraction)  │                       │  (Chunking & Embed)   │
     └───────────┬───────────┘                       └───────────┬───────────┘
                 │                                               │
                 ▼                                               ▼
     ┌───────────────────────┐                       ┌───────────────────────┐
     │    Neo4j Database     │                       │      FAISS + BM25     │
     │  (Bolt: localhost:7687│                       │   (Dense/Sparse Store)│
     └───────────┬───────────┘                       └───────────┬───────────┘
                 │                                               │
                 └───────────────────────┬───────────────────────┘
                                         │
                                         ▼
                             ┌───────────────────────┐
                             │     rag_search.py     │
                             │ (Hybrid GraphRAG Core)│
                             └───────────┬───────────┘
                                         │
                                         ▼
                             ┌───────────────────────┐
                             │      webhook.py       │
                             │ (Flask LINE Bot API)  │
                             └───────────┬───────────┘
                                         │
                                         ▼
                             ┌───────────────────────┐
                             │   LINE Messaging App  │
                             └───────────────────────┘
```

---

## 2. ขั้นตอนการรันระบบ (Step-by-Step Operations)

### ขั้นตอนที่ 1: สตาร์ท Neo4j Database
ตรวจสอบว่า Docker Desktop เปิดอยู่ แล้วรันคำสั่ง:
```bash
docker compose up -d
```
* เข้าใช้งาน Web UI ได้ที่: `http://localhost:7474` (User: `neo4j`, Password: `password1234`)
* พอร์ตการเชื่อมต่อ Bolt: `bolt://localhost:7687`

---

### ขั้นตอนที่ 2: Ingest ข้อมูล Knowledge Graph เข้า Neo4j
ประมวลผลข้อมูลจาก `documents.pdf` เข้าสู่ Neo4j (มีให้เลือก 2 รูปแบบ):

* **แบบที่ 1: แบบความเร็วสูง (SBERT Salient Filter - แนะนำสำหรับการทำงานรวดเร็ว 3–5 วินาที)**
  ```bash
  python feed_graph.py
  ```

* **แบบที่ 2: แบบใช้ LLM ร่วมสกัด (LLM-Enriched Mode ด้วย Ollama `qwen2.5:7b`)**
  ```bash
  python feed_graph.py --llm
  ```
  *(ระบบจะให้ `qwen2.5:7b` สรุปเนื้อหาสำคัญทุกหน้าลงใน `page_knowledge.json` และนำเข้า Neo4j)*

ตรวจสอบความถูกต้องและสถิติของกราฟ:
```bash
python check_graph.py
```

---

### ขั้นตอนที่ 3: สร้าง FAISS Vector Index (สำหรับ Hybrid Search)
หั่นข้อความจาก `documents.pdf` และแปลงเป็น Embeddings เก็บลงโฟลเดอร์ `faiss_index/`:
```bash
python build_index.py
```

---

### ขั้นตอนที่ 4: ทดสอบค้นหาผ่าน Hybrid RAG (ทางเลือก)
ทดสอบการทำงานของ RAG (FAISS + BM25 + Neo4j Cypher + LLM) บน Terminal:
```bash
python rag_search.py
```

---

### ขั้นตอนที่ 5: การรัน Webhook ร่วมกับ Cloudflare Tunnel (แยก 2 Terminal)

เพื่อให้ LINE Platform สามารถส่งข้อความจากมือถือเข้ามาหาโค้ดในเครื่องของเราได้ ต้องเปิดใช้งาน 2 Terminal ควบคู่กัน:

#### 🖥️ Terminal ที่ 1: รัน Webhook Server (Flask)
เปิด Terminal ที่ 1 ไปที่โฟลเดอร์โปรเจกต์ แล้วรันคำสั่ง:
```powershell
python webhook.py
```
* เซิร์ฟเวอร์จะเริ่มต้นทำงานที่พอร์ต `5000` (รอรับ Request ที่ `http://127.0.0.1:5000`)
* มี Endpoint สำคัญคือ `/callback` (สำหรับรับข้อความจาก LINE) และ `/query` (สำหรับทดสอบ)

---

#### 🌐 Terminal ที่ 2: รัน Cloudflare Tunnel (สร้าง Public HTTPS URL)
เปิด Terminal ที่ 2 (ไม่ต้องปิด Terminal ที่ 1) แล้วรันคำสั่ง:
```powershell
cloudflared tunnel --url http://localhost:5000
```
> **หมายเหตุ:** หากยังไม่ได้ติดตั้ง Cloudflare Tunnel บนเครื่อง สามารถดาวน์โหลด `cloudflared.exe` หรือติดตั้งผ่าน winget:
> ```powershell
> winget install --id Cloudflare.cloudflared
> ```

เมื่อคำสั่งทำงาน สังเกตใน Terminal ที่ 2 จะมีข้อความแสดง URL ชั่วคราวที่ลงท้ายด้วย `.trycloudflare.com` เช่น:
```
+--------------------------------------------------------------------------------------------+
|  Your quick Tunnel has been created! Visit it at (it may take some time to be reachable):  |
|  https://example-random-subdomain.trycloudflare.com                                        |
+--------------------------------------------------------------------------------------------+
```

---

#### 📲 ขั้นตอนที่ 6: นำ URL ไปตั้งค่าใน LINE Developers Console

1. นำ URL ที่ได้จาก Cloudflare Tunnel ใน Terminal ที่ 2 มาต่อท้ายด้วย `/callback` เช่น:
   ```
   https://example-random-subdomain.trycloudflare.com/callback
   ```
2. เข้าสู่ [LINE Developers Console](https://developers.line.biz/) $\rightarrow$ เลือก Channel ของคุณ
3. ไปที่แท็บ **Messaging API**
4. ในส่วน **Webhook settings**:
   * วาง URL ลงในช่อง **Webhook URL** แล้วกด **Update**
   * กดปุ่ม **Verify** $\rightarrow$ ระบบต้องแสดงข้อความ **Success**
   * สลับสวิตช์ **Use webhook** เป็น **ON**
5. ไปที่ [LINE Official Account Manager](https://manager.line.biz/):
   * เมนู **ตั้งค่าการตอบกลับ (Response settings)**
   * ปิด **ข้อความตอบกลับอัตโนมัติ (Auto-response messages)** ให้เป็น **OFF** (เพื่อไม่ให้ข้อความระบบของ LINE แทรกแซงคำตอบของบอท)
6. ทดลองพิมพ์คุยกับบอทในแอป LINE บนมือถือได้ทันที! ☕

---

## 3. ตัวอย่างคำถามทดสอบสำหรับบาริสต้า (Sample Queries)

| หมวดหมู่คำถาม | ตัวอย่างคำถามที่สามารถถามบอทได้ |
|---|---|
| **ขอสูตรและขั้นตอน** | "ขอสูตรกาแฟส้มหน่อย ใช้วัตถุดิบอะไรบ้างและทำอย่างไร" |
| **สูตร Moka Pot** | "อยากทำกาแฟพีช ใช้ Moka Pot บดเบอร์ไหนและต้มยังไง" |
| **แก้ปัญหากาแฟเปรี้ยว** | "กาแฟรสชาติเปรี้ยวโดด ครีมม่าบาง น้ำไหลเร็ว เกิดจากอะไร แก้ยังไง" |
| **แก้ปัญหากาแฟขมไหม้** | "กาแฟรสขมจัด มีกลิ่นไหม้ น้ำหยดช้า เกิดจากสาเหตุอะไรและมีวิธีแก้ยังไง" |
| **เปรียบเทียบสายพันธุ์** | "อาราบิก้ากับโรบัสต้าต่างกันอย่างไร และปลูกที่ความสูงเท่าไหร่" |
| **วิทยาศาสตร์การคั่ว** | "ระดับการคั่วแบบ Agtron คืออะไร และ Pyrolysis เกิดขึ้นที่กี่องศา" |
| **วิทยาศาสตร์ฟองนม** | "การสตีมนมทำไมโครโฟมต้องใช้อุณหภูมิเท่าไหร่ และลาย Free Pour มีอะไรบ้าง" |
| **แนวข้อสอบบาริสต้า** | "ข้อสอบ: จงอธิบายเคล็ดลับและเทคนิคในการชงเครื่องดื่ม" |
| **รีเซ็ตประวัติการคุย** | "ล้างประวัติ" หรือ "รีเซ็ต" |

