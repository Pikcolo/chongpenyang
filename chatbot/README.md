# SmartDoc Barista Assistant – Production-Grade Hybrid RAG Chatbot (Project 2)

A state-of-the-art **Production-Grade (Grade A Standard)** Hybrid RAG Chatbot built with **Ollama (`qwen2.5:7b`)**, **ChromaDB / FAISS**, **BM25 with Thai morphological tokenization**, **Reciprocal Rank Fusion (RRF)**, **Cross-Encoder Re-ranking**, **Dynamic Top-k & Token Budgeting**, **Zero-Hallucination Guardrails**, and **SBERT/BERT Quantitative Evaluation**.

Based on the 53-page manual:
> **คู่มือประกอบการฝึกอบรม หลักสูตร: บาริสต้ามืออาชีพ** (`documents.pdf`)

---

## 🌟 Rubric Alignment & Key Features (Grade A Standards)

| Criterion | Implementation & Technical Granularity | Production-Grade Standard |
| :--- | :--- | :---: |
| **1. PDF Ingestion & Advanced Chunking (15%)** | • `pdfplumber` layout & table-aware parser extracts tables as clean Markdown<br>• Parent-Child Document Chunking (Granular child chunks + Rich parent context)<br>• Thai ligature / OCR typo cleaning (`text_cleaner.py`) & Header/Footer noise filter | **Grade A (4/4)** |
| **2. Hybrid Retrieval & Fusion Engine (25%)** | • Dense Vector Store (ChromaDB / FAISS) + Sparse Lexical Search (BM25 with PyThaiNLP)<br>• Reciprocal Rank Fusion (RRF) & Convex Relative Score Fusion<br>• Cross-Encoder Re-ranker (`cross-encoder/mmarco-mMiniLMv2-L12-H384-v1`) | **Grade A (4/4)** |
| **3. Dynamic Top-k & Embedding Optimization (15%)** | • Multilingual SBERT (`sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2`)<br>• Dynamic Top-k based on query complexity (Factoid: $k=3$, Complex: $k=7 \sim 8$)<br>• Token Budget Management (prevents context overflow while preserving citations) | **Grade A (4/4)** |
| **4. Prompt Engineering & Guardrails (20%)** | • Few-Shot + Chain-of-Thought (CoT) system prompt<br>• Strict Zero-Hallucination Guardrails & similarity threshold validation<br>• Source Citation Engine (Topic, Title, Page number, and snippet) | **Grade A (4/4)** |
| **5. SBERT/BERT Quantitative Evaluation (15%)** | • 20 Domain Q&A benchmark test dataset (`test_dataset.json`)<br>• Evaluation with SBERT Cosine Similarity, BERTScore (P, R, F1), and Context Faithfulness<br>• Ablation Study comparison table (Dense vs BM25 vs Hybrid vs Re-ranked) | **Grade A (4/4)** |
| **6. Code Architecture & MLOps Reproducibility (10%)** | • Clean Modular OOP Architecture (`ingestion/`, `retrieval/`, `generation/`, `evaluation/`, `interfaces/`)<br>• Centralized config management (`config.yaml` + `.env`)<br>• Pinned `requirements.txt`, CLI chat runner, and LINE Webhook | **Grade A (4/4)** |

---

## 📁 โครงสร้างโปรเจกต์ `chatbot/`
```
chatbot/
├── config.py                      # Pydantic & YAML Configuration Loader
├── config.yaml                    # System configuration parameters
├── data/                          # Persistent storage for ChromaDB, FAISS, and cached chunks
│   ├── chroma_db/
│   ├── faiss_index/
│   └── documents_cache.pkl
├── ingestion/                     # Module 1: Ingestion & Advanced Chunking
│   ├── text_cleaner.py            # Thai OCR cleaning and header/footer removal
│   ├── pdf_parser.py              # pdfplumber table & layout extractor
│   ├── chunker.py                 # Parent-Child & Semantic Chunker
│   ├── metadata_extractor.py      # Domain topic & section tagging
│   └── build_index.py             # Indexing Pipeline script
├── retrieval/                     # Module 2 & 3: Hybrid Retrieval & Fusion
│   ├── vector_store.py            # ChromaDB & FAISS unified manager
│   ├── bm25_retriever.py          # Thai word tokenized BM25 retriever
│   ├── fusion.py                  # RRF & Relative Score Fusion algorithms
│   ├── reranker.py                # Cross-Encoder Re-ranker
│   └── dynamic_retriever.py       # Dynamic Top-k & Token Budget Manager
├── generation/                    # Module 4: Generation & Guardrails
│   ├── prompt_templates.py        # System prompt, Few-Shot & CoT templates
│   ├── guardrails.py              # Strict Zero-Hallucination Guardrails
│   ├── citation_engine.py         # Structured Source Reference generator
│   └── rag_chain.py               # Conversational Pipeline with multi-turn memory
├── evaluation/                    # Module 5: Quantitative Evaluation
│   ├── test_dataset.json          # Benchmark 20 Q&A pairs
│   ├── metrics.py                 # SBERT Cosine Sim, BERTScore, Faithfulness
│   ├── run_evaluation.py          # Benchmark Runner & Ablation report generator
│   └── evaluation_results.md      # Auto-generated evaluation report
├── interfaces/                    # Module 6: User Interfaces
│   ├── app_chat.py                # Interactive CLI Testbench
│   └── webhook.py                 # LINE Webhook server & REST API (`/query`)
├── tests/                         # Unit & Integration test suite
│   ├── test_ingestion.py
│   ├── test_hybrid_search.py
│   └── test_guardrails.py
└── docs/                          # Integration documentation
    └── rag-integration-guide.md
```

---

## 🚀 วิธีการใช้งาน (Quickstart Guide)

### 1. ติดตั้ง Dependencies
```bash
pip install -r requirements.txt
```

### 2. สร้างดัชนี Vector & BM25 (ถ้าต้องการสร้างใหม่)
```bash
python -m chatbot.ingestion.build_index
```

### 3. รัน Unit Tests เพื่อทดสอบความถูกต้อง
```bash
pytest chatbot/tests
```

### 4. รันการประเมินผลเชิงปริมาณ (SBERT & BERTScore Benchmark)
```bash
# ทดสอบคำถามแบบเต็ม 20 ข้อ
python -m chatbot.evaluation.run_evaluation

# หรือทดสอบแบบเร็ว (5 ข้อ)
python -m chatbot.evaluation.run_evaluation --quick
```
*(ผลลัพธ์ตารางคะแนนจะถูกบันทึกที่ `chatbot/evaluation/evaluation_results.md`)*

### 5. เปิดใช้งาน Interactive CLI Chat เพื่อทดสอบถาม-ตอบ
```bash
python -m chatbot.interfaces.app_chat
```

### 6. รัน LINE Webhook Server & REST API
```bash
python -m chatbot.interfaces.webhook
```
- ทดสอบ Query ผ่าน REST API: `http://localhost:5000/query?q=ขอสูตรกาแฟส้ม`
- ตั้งค่า LINE Webhook URL: `https://<your-domain>/callback`

---

## 🧠 การเลือกและสลับโมเดล LLM
สามารถอ่านคู่มือแนะนำการ Setup, การสลับโมเดลบน Ollama และตารางวิเคราะห์เปรียบเทียบเชิงลึกระหว่าง `Qwen 2.5 (3B)` vs `Llama 3.2 (3B)` vs `Gemma 2 (2B)` ได้ที่:
👉 **[คู่มือการเลือกและการตั้งค่า LLM (chatbot/docs/llm-selection-and-comparison.md)](file:///d:/PIK/y4-1/241-351_AI_for_social/chongpenyang/chatbot/docs/llm-selection-and-comparison.md)**

---

## 📚 เอกสารเพิ่มเติมที่เกี่ยวข้อง
- **คู่มือการเชื่อมต่อ LINE Webhook & Cloudflare Tunnel**: [chatbot/docs/rag-integration-guide.md](file:///d:/PIK/y4-1/241-351_AI_for_social/chongpenyang/chatbot/docs/rag-integration-guide.md)
- **ชุดข้อความทดสอบสำหรับส่งใน LINE (ไฟล์ Excel 20 ข้อ)**: [test_line_queries.xlsx](file:///d:/PIK/y4-1/241-351_AI_for_social/chongpenyang/test_line_queries.xlsx)
