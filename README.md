# Coffee Barista AI: Knowledge Graph (Neo4j) & Production-Grade Hybrid RAG (Project 2)

A modular monorepo system containing:
1. **Neo4j Knowledge Graph** (`knowledge-graph/`): Domain ontology with 359 nodes and 773 relationships modeling coffee botany, processing, roasting, extraction troubleshooting, and recipes.
2. **Production-Grade Hybrid RAG Chatbot** (`chatbot/`): Grade A certified RAG system with ChromaDB/FAISS dense search, BM25 sparse search, Reciprocal Rank Fusion (RRF), Cross-Encoder Re-ranking, Dynamic Top-k, Zero-Hallucination Guardrails, and SBERT/BERT quantitative evaluation.

Based on the 53-page manual:
> **คู่มือประกอบการฝึกอบรม หลักสูตร: บาริสต้ามืออาชีพ** (`documents.pdf`)

---

## 📁 โครงสร้างโปรเจกต์ (Monorepo Structure)

```
chongpenyang/
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
    ├── data/                          # Persistent ChromaDB, FAISS & BM25 indices
    ├── ingestion/                     # Layout/table parser, text cleaner & Parent-Child chunking
    ├── retrieval/                     # Dense (Chroma/FAISS) + Sparse (BM25) + RRF + Cross-Encoder
    ├── generation/                    # CoT prompt templates, Zero-Hallucination guardrails & citations
    ├── evaluation/                    # 20 Q&A benchmark dataset, SBERT & BERTScore evaluator
    ├── interfaces/                    # Interactive CLI testbench & LINE Webhook server
    ├── tests/                         # Unit tests (Ingestion, Hybrid search, Guardrails)
    └── README.md                      # Detailed technical guide for Chatbot
```

---

## 🚀 การเริ่มต้นใช้งานแบบรวดเร็ว (Quickstart Guide)

### 1. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 2. รันส่วน Knowledge Graph (Neo4j)
```bash
cd knowledge-graph
docker compose up -d
python check_graph.py
pytest tests/test_kg.py
cd ..
```

### 3. รันส่วน Hybrid RAG Chatbot (Project 2)
```bash
# 3.1 รัน Unit Tests เพื่อทดสอบความถูกต้อง
pytest chatbot/tests

# 3.2 ทดสอบแชทผ่าน Interactive CLI
python -m chatbot.interfaces.app_chat

# 3.3 รันการประเมินผลเชิงปริมาณ (SBERT & BERTScore)
python -m chatbot.evaluation.run_evaluation --quick

# 3.4 รัน LINE Webhook Server & REST API
python -m chatbot.interfaces.webhook
```
*(ทดสอบ REST API Endpoint: `http://localhost:5000/query?q=ขอสูตรกาแฟส้ม`)*

---

## 📚 เอกสารอ้างอิงเชิงลึก (In-Depth Documentation)
- **ชุดข้อความทดสอบสำหรับ LINE (Excel)**: ดาวน์โหลดไฟล์ข้อความทดสอบ 20 ข้อพร้อมคำตอบที่คาดหวังได้ที่ [test_line_queries.xlsx](file:///d:/PIK/y4-1/241-351_AI_for_social/chongpenyang/test_line_queries.xlsx)
- **การเลือกและเปรียบเทียบโมเดล LLM**: อ่านคู่มือวิเคราะห์เปรียบเทียบ `Qwen 2.5 (3B)` vs `Llama 3.2 (3B)` vs `Gemma 2 (2B)` ได้ที่ [chatbot/docs/llm-selection-and-comparison.md](file:///d:/PIK/y4-1/241-351_AI_for_social/chongpenyang/chatbot/docs/llm-selection-and-comparison.md)
- **โครงสร้าง Knowledge Graph**: อ่านรายละเอียด Schema และ Cypher ได้ที่ [knowledge-graph/docs/graph-schema.md](file:///d:/PIK/y4-1/241-351_AI_for_social/chongpenyang/knowledge-graph/docs/graph-schema.md)
- **การเชื่อมต่อ LINE Bot & Webhook**: อ่านได้ที่ [chatbot/docs/rag-integration-guide.md](file:///d:/PIK/y4-1/241-351_AI_for_social/chongpenyang/chatbot/docs/rag-integration-guide.md)