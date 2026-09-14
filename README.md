# SmartDoc Assistant – Coffee Barista Knowledge Graph & Hybrid RAG LINE Chatbot

A production-grade **Knowledge Graph and Hybrid RAG System** built with **Neo4j**, **FAISS**, **BM25**, and **LINE Messaging API** based on the 53-page manual:
> **คู่มือประกอบการฝึกอบรม หลักสูตร: บาริสต้ามืออาชีพ** (`documents.pdf`)

Developed for Course **241-351 AI for Social Good** (SmartDoc Assistant Project).

---

## 🌟 Features

- **Domain-Rich Knowledge Graph (Neo4j)**:
  - **359 Nodes & 773 Relationships** modeling coffee botany, 10 stages from tree to cup, roasting levels (Agtron), grind sizing, extraction science (Perfect vs Under vs Over), latte art techniques, and 13 full recipes (Hot & Cold coffees).
  - Standard Operating Procedures (SOPs), ingredient ratios, equipment, and troubleshooting diagnostics.
- **Hybrid Retrieval-Augmented Generation (GraphRAG)**:
  - **Dense Vector Search**: FAISS index powered by `sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`.
  - **Lexical Keyword Search**: BM25 with Thai morphological word segmentation (`pythainlp`).
  - **Graph Traversal**: Direct Cypher queries for relational accuracy (ingredients, equipment, SOP steps, extraction causes & solutions).
- **Conversational Memory**:
  - Multi-turn conversation tracking with pronoun resolution support (e.g. "มัน", "เมนูนี้").
- **LINE Webhook Integration**:
  - Real-time chatbot webhook for LINE Messaging API.
  - Testable REST API endpoint for local debugging.

---

## 📁 Repository Structure

```
chongpenyang/
├── documents.pdf                  # Source 53-page Barista Training Manual
├── docker-compose.yml             # Neo4j 5 Community container orchestration
├── .env                           # Environment configuration
├── .env.example                   # Example configuration template
├── requirements.txt               # Dependencies list
├── feed_graph.py                  # Knowledge extractor & Neo4j ingestion engine
├── check_graph.py                 # Graph statistics & Cypher verification script
├── build_index.py                 # PDF chunker & FAISS vector store builder
├── rag_search.py                  # Hybrid RAG search engine (FAISS + BM25 + Neo4j + LLM)
├── webhook.py                     # LINE Bot webhook server & REST API
├── page_knowledge.json            # Extracted structured JSON knowledge base
├── faiss_index/                   # Serialized FAISS vector index
├── docs/
│   ├── graph-schema.md            # Domain Ontology Diagram & Cypher visualization queries
│   ├── knowledge-graph-summary.md # Comprehensive Knowledge Graph & Ontology data analysis
│   └── rag-integration-guide.md   # Deployment, operation & LINE setup guide
└── tests/
    └── test_kg.py                 # Automated test suite
```

---

## 🚀 Quickstart Guide

### 1. Start Neo4j
```bash
docker compose up -d
```
Neo4j Browser UI will be available at: `http://localhost:7474` (User: `neo4j`, Password: `password1234`).

### 2. Ingest Knowledge Graph into Neo4j
```bash
# Fast Mode (SBERT Salient Keyword Filter - 3–5 seconds)
python feed_graph.py

# Or Full LLM Mode (Summarization via Ollama qwen2.5:7b)
python feed_graph.py --llm
```

### 3. Verify Graph Data
```bash
python check_graph.py
```

### 4. Build Vector Index
```bash
python build_index.py
```

### 5. Test Hybrid RAG Search
```bash
python rag_search.py
```

### 6. Run LINE Bot Webhook Server & Cloudflare Tunnel (2 Terminals)

เพื่อให้ LINE Webhook สามารถยิงเข้ามาหา Server บนเครื่อง Local ได้ ให้เปิด **2 Terminal** ควบคู่กัน:

#### 🖥️ Terminal 1: รัน Webhook Server (Flask)
```powershell
python webhook.py
```
*(เซิร์ฟเวอร์จะรันที่ `http://127.0.0.1:5000`)*

#### 🌐 Terminal 2: รัน Cloudflare Tunnel
```powershell
cloudflared tunnel --url http://localhost:5000
```
*(คัดลอก URL ที่ได้ เช่น `https://xxxx.trycloudflare.com` แล้วนำไปต่อท้ายเป็น `https://xxxx.trycloudflare.com/callback` ใส่ลงใน **LINE Developers Console** -> **Webhook URL** จากนั้นกด **Verify** และเปิด **Use Webhook**)*

---

### 7. Test Locally via HTTP API
```bash
curl -X POST http://localhost:5000/query \
     -H "Content-Type: application/json" \
     -d "{\"question\": \"ขอสูตรกาแฟส้มหน่อย\"}"
```