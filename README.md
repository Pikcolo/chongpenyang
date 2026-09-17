# ☕ Coffee Barista AI: Knowledge Graph (Neo4j) & Production-Grade Hybrid RAG (Project 2)

A production-grade, modular monorepo system containing:
1. **Neo4j Knowledge Graph** (`knowledge-graph/`): Domain ontology with 359 nodes and 773 relationships modeling coffee botany, processing, roasting, extraction troubleshooting, and recipes.
2. **Production-Grade Hybrid RAG & Chatbot** (`chatbot/`): Grade A certified RAG system with ChromaDB/FAISS dense search, BM25 sparse search, Reciprocal Rank Fusion (RRF), Cross-Encoder Re-ranking, Dynamic Top-k, Zero-Hallucination Guardrails, and SBERT/BERT quantitative evaluation.
3. **Web Simulator & Diagnostics Inspector** (`chatbot/web/`): Interactive Web UI with real-time RAG telemetry, animated Thinking UI, Assistant Cards, and 1-Click test prompts.
4. **LINE UI Ecosystem** (`chatbot/line_ui/`): Official 6-grid Rich Menu (2500x1686 custom barista art with auto-deploy script), Contextual Quick Replies (strictly <= 20 chars), 8-Drink Flex Message Carousel, and Extraction Troubleshoot Card.

Based on the 53-page official training manual:
> **คู่มือประกอบการฝึกอบรม หลักสูตร: บาริสต้ามืออาชีพ** (`documents.pdf`)

---

## 📁 โครงสร้างโปรเจกต์ (Monorepo Structure)

```
chongpenyang/
├── main.py                            # [Entry Point] รัน Unified Server (Web Simulator + LINE Webhook)
├── setup_rich_menu.py                 # [Utility] สร้างและลงทะเบียน LINE Rich Menu 6 ช่องอัตโนมัติ
├── test_line_queries.json             # [Dataset] ชุดทดสอบ 20 คำถามสำหรับ LINE Bot พร้อมคำตอบที่คาดหวัง
├── documents.pdf                      # [Shared] เอกสารต้นฉบับ 53 หน้า "คู่มือบาริสต้ามืออาชีพ"
├── .env                               # [Shared] Environment Variables (Ollama, LINE, Neo4j, DB paths)
├── .env.example                       # [Shared] Example Template Configuration
├── config.yaml                        # [Shared] YAML Configuration parameters
├── requirements.txt                   # [Shared] Pinned production dependencies
├── README.md                          # [Shared] Master Monorepo Documentation
│
├── knowledge-graph/                   # [KG Module] Neo4j Knowledge Graph System
│   ├── docker-compose.yml             # Neo4j 5 Community container orchestration
│   ├── feed_graph.py                  # Knowledge Extractor & Neo4j Ingestion Engine
│   ├── check_graph.py                 # Graph statistics & Cypher verification
│   ├── page_knowledge.json            # Extracted structured JSON ontology
│   ├── neo4j_db/                      # Persistent database volume directory
│   ├── docs/                          # Graph-specific documentation
│   │   ├── graph-schema.md            # Ontology Diagram & Cypher queries
│   │   └── knowledge-graph-summary.md # 359 Nodes & 773 Relationships analysis
│   ├── tests/
│   │   └── test_kg.py                 # KG Automated Test Suite
│   └── README.md                      # KG usage & setup guide
│
└── chatbot/                           # [Chatbot Module] Production-Grade Hybrid RAG (Project 2)
    ├── config.py                      # Unified configuration loader
    ├── config.yaml                    # Chatbot settings
    ├── data/                          # Persistent FAISS vector store & BM25 indices
    ├── ingestion/                     # Layout/table parser, text cleaner & Parent-Child chunking
    ├── retrieval/                     # Dense (FAISS) + Sparse (BM25) + RRF + Cross-Encoder
    ├── generation/                    # CoT prompt templates, Zero-Hallucination guardrails & citations
    ├── evaluation/                    # 20 Q&A benchmark dataset, SBERT & BERTScore evaluator
    ├── line_ui/                       # LINE UI Components (Rich Menu, Quick Replies, Flex Carousels)
    │   ├── rich_menu.py               # 6-grid 2500x1686 Custom Art Processor & LINE API payload
    │   ├── quick_replies.py           # Contextual Quick Replies (5 Modules Taxonomy)
    │   ├── flex_carousel.py           # Popular drink recipes carousel flex message
    │   ├── flex_troubleshoot.py       # Under vs Over Extraction diagnostic flex card
    │   └── flex_welcome.py            # Welcome flex message
    ├── web/                           # Web Simulator & Real-time RAG Inspector
    │   ├── templates/index.html       # 2-Column Dashboard (Inspector Sidebar + Chat Simulator)
    │   └── static/                    # CSS, JS, images (rich_menu_barista.png, rich_menu_line.jpg)
    ├── interfaces/                    # Unified Flask Server & LINE Webhook
    │   ├── webhook.py                 # Server handling Web Simulator at '/' and LINE at '/callback'
    │   └── app_chat.py                # Terminal Interactive CLI
    ├── docs/                          # Technical Documentation
    │   ├── rag-integration-guide.md   # Complete Web Simulator & LINE Integration Guide
    │   └── llm-selection-and-comparison.md # LLM benchmark (Qwen 2.5 3B vs Llama 3.2 vs Gemma 2)
    └── tests/                         # Unit tests (Ingestion, Hybrid search, Guardrails)
```

---

## 🚀 การเริ่มต้นใช้งานแบบรวดเร็ว (Quickstart Guide)

### 1. ติดตั้ง Dependencies & เตรียม Environment
```bash
pip install -r requirements.txt
```

### 2. ตั้งค่า LINE Rich Menu (ทำเพียงครั้งแรก)
```bash
python setup_rich_menu.py
```
*ระบบจะสร้างภาพ 2500x1686, ลงทะเบียนกับ LINE และเปิดใช้งาน Default Rich Menu ทันที*

### 3. รัน Server หลัก (Web Simulator & LINE Webhook)
```bash
python main.py
```
- **เปิดใช้งาน Web Simulator & Inspector:** เข้าเบราว์เซอร์ไปที่ `http://localhost:5000`
- **เปิด Cloudflare Tunnel สำหรับ LINE Bot:**
  ```bash
  cloudflared tunnel --url http://localhost:5000
  ```
  นำ URL `https://xxxx.trycloudflare.com/callback` ไปใส่ใน LINE Developers Console

### 4. รันการประเมินผลเชิงปริมาณ (SBERT & BERTScore Quantitative Evaluation)
```bash
python -m chatbot.evaluation.run_evaluation --quick
```

---

## 📚 เอกสารประกอบการเรียนรู้และอ้างอิง (Documentation Index)

- **คู่มือการติดตั้ง Web Simulator & เชื่อมต่อ LINE Bot**: [chatbot/docs/rag-integration-guide.md](file:///d:/PIK/y4-1/241-351_AI_for_social/chongpenyang/chatbot/docs/rag-integration-guide.md)
- **ชุดข้อความทดสอบสำหรับ LINE (JSON 20 ข้อ)**: [test_line_queries.json](file:///d:/PIK/y4-1/241-351_AI_for_social/chongpenyang/test_line_queries.json)
- **การเลือกและเปรียบเทียบโมเดล LLM**: [chatbot/docs/llm-selection-and-comparison.md](file:///d:/PIK/y4-1/241-351_AI_for_social/chongpenyang/chatbot/docs/llm-selection-and-comparison.md)
- **สถาปัตยกรรมและ Schema ของ Knowledge Graph (Neo4j)**: [knowledge-graph/docs/knowledge-graph-summary.md](file:///d:/PIK/y4-1/241-351_AI_for_social/chongpenyang/knowledge-graph/docs/knowledge-graph-summary.md)