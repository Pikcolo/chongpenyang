import os
import sys
from dotenv import load_dotenv

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

import pythainlp
from rank_bm25 import BM25Okapi
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS
from langchain_ollama import ChatOllama
from neo4j import GraphDatabase

# ============================================================
# 1. LOAD CONFIGURATION FROM .ENV
# ============================================================

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH", "documents.pdf")
FAISS_PATH = os.getenv("FAISS_PATH", "faiss_index")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
LLM_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
TOP_K = int(os.getenv("TOP_K", "6"))

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

if not NEO4J_URI or not NEO4J_PASSWORD:
    raise ValueError("❌ กรุณากำหนด NEO4J_URI และ NEO4J_PASSWORD ในไฟล์ .env ให้ครบถ้วน")

# ============================================================
# 2. INITIALIZE VECTORSTORE, BM25 & NEO4J
# ============================================================

print("Initializing Hybrid RAG Pipeline...")

# Load FAISS dense vectorstore
embeddings = HuggingFaceEmbeddings(
    model_name=EMBED_MODEL,
    model_kwargs={'device': 'cpu'}
)

if os.path.exists(FAISS_PATH):
    vectorstore = FAISS.load_local(FAISS_PATH, embeddings, allow_dangerous_deserialization=True)
    doc_dict = vectorstore.docstore._dict
    chunks = list(doc_dict.values())
else:
    chunks = []
    vectorstore = None

# Initialize BM25 sparse index
if chunks:
    tokenized_corpus = [pythainlp.word_tokenize(c.page_content, engine='newmm') for c in chunks]
    bm25 = BM25Okapi(tokenized_corpus)
else:
    bm25 = None

# Connect to Neo4j Graph Database
try:
    neo4j_driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    with neo4j_driver.session() as s:
        s.run("RETURN 1")
    print("✅ Neo4j connection established.")
except Exception as e:
    print(f"⚠️ Neo4j Connection Error: {e}")
    neo4j_driver = None

# Initialize Ollama LLM
try:
    llm = ChatOllama(model=LLM_MODEL, temperature=0.1)
except Exception as e:
    print(f"⚠️ Ollama Init Note: {e}")
    llm = None

# ============================================================
# 3. HYBRID RETRIEVAL FUNCTIONS
# ============================================================

def hybrid_search_documents(question: str, top_k: int = TOP_K):
    """Combines FAISS dense vector search and BM25 sparse keyword search."""
    if not vectorstore or not bm25 or not chunks:
        return []

    # 1. FAISS Search
    faiss_docs = vectorstore.similarity_search(question, k=top_k)

    # 2. BM25 Search
    q_tokens = pythainlp.word_tokenize(question, engine='newmm')
    bm25_scores = bm25.get_scores(q_tokens)
    top_bm25_indices = sorted(range(len(bm25_scores)), key=lambda i: bm25_scores[i], reverse=True)[:top_k]
    bm25_docs = [chunks[i] for i in top_bm25_indices if bm25_scores[i] > 0]

    # Interleave and deduplicate
    combined = []
    seen = set()
    for d in bm25_docs + faiss_docs:
        cid = d.metadata.get('chunk_id')
        if cid not in seen:
            seen.add(cid)
            combined.append(d)
        if len(combined) >= top_k:
            break
    return combined

def search_graph_context(question: str) -> str:
    """Queries Neo4j Knowledge Graph for recipes, extraction science, species, and techniques."""
    if not neo4j_driver:
        return "ไม่พบข้อมูลความสัมพันธ์ใน Graph (Database offline)"

    tokens = [w for w in pythainlp.word_tokenize(question, engine='newmm') if len(w.strip()) > 1]
    graph_facts = []

    # Filter out generic words to avoid matching all coffee drinks on the word 'กาแฟ'
    generic_stopwords = {'กาแฟ', 'เครื่องดื่ม', 'สูตร', 'ขอ', 'หน่อย', 'วิธี', 'ทำ', 'ชง', 'แก้ว', 'เมนู', 'มี', 'อะไร', 'บ้าง', 'ครับ', 'ค่ะ', 'ใส', 'ใส่อะไร', 'อยากได้'}
    distinctive_tokens = [w for w in tokens if w not in generic_stopwords] or tokens

    with neo4j_driver.session() as session:
        # 1. Beverage Recipe Match
        q_recipe = """
        MATCH (b:Beverage)
        WHERE any(t IN $tokens WHERE b.name CONTAINS t) OR $search_text CONTAINS b.name
        OPTIONAL MATCH (b)-[ri:USES_INGREDIENT]->(i:Ingredient)
        OPTIONAL MATCH (b)-[:USES_EQUIPMENT]->(eq:Equipment)
        OPTIONAL MATCH (b)-[:HAS_STEP]->(st:RecipeStep)
        RETURN b.name AS name,
               b.category AS category,
               b.roast_recommendation AS roast,
               b.grind_recommendation AS grind,
               b.tips AS tips,
               collect(DISTINCT i.name + ' (' + ri.amount + ' ' + ri.unit + ')') AS ingredients,
               collect(DISTINCT eq.name) AS equipment,
               collect(DISTINCT toString(st.step_number) + '. ' + st.action) AS steps
        """
        recipes = session.run(q_recipe, {"tokens": distinctive_tokens, "search_text": question}).data()
        for r in recipes:
            ing_str = ', '.join(r['ingredients']) if r['ingredients'] else 'ตามสัดส่วนมาตรฐาน'
            eq_str = ', '.join(r['equipment']) if r['equipment'] else 'อุปกรณ์มาตรฐาน'
            sorted_steps = ' | '.join(sorted(r['steps'])) if r['steps'] else 'ดูขั้นตอนในเอกสาร'
            graph_facts.append(
                f"[สูตรเครื่องดื่ม: {r['name']}] หมวดหมู่: {r['category']} | ระดับคั่ว: {r['roast']} | เบอร์บด: {r['grind']}\n"
                f"  - วัตถุดิบ: {ing_str}\n"
                f"  - อุปกรณ์: {eq_str}\n"
                f"  - ขั้นตอน: {sorted_steps}\n"
                f"  - เคล็ดลับ: {r['tips']}"
            )

        # 2. Extraction Troubleshooting Match
        if any(w in question for w in ['เปรี้ยว', 'ขม', 'สกัด', 'ครีมม่า', 'under', 'over', 'perfect', 'ไหลเร็ว', 'ไหลช้า', 'หยด']):
            q_ext = """
            MATCH (ex:ExtractionStatus)
            RETURN ex.status AS status, ex.crema AS crema, ex.taste AS taste,
                   ex.causes AS causes, ex.solutions AS solutions
            """
            ext_data = session.run(q_ext).data()
            for ex in ext_data:
                graph_facts.append(
                    f"[การสกัด: {ex['status']}]\n"
                    f"  - ครีมม่า: {ex['crema']}\n"
                    f"  - รสชาติ: {ex['taste']}\n"
                    f"  - สาเหตุ: {ex['causes']}\n"
                    f"  - แนวทางแก้ไข: {ex['solutions']}"
                )

        # 3. Coffee Species Match
        if any(w in question for w in ['อาราบิก้า', 'โรบัสต้า', 'arabica', 'robusta', 'peaberry', 'สายพันธุ์', 'พันธุ์', 'ปลูก']):
            q_species = """
            MATCH (s:Species)
            OPTIONAL MATCH (s)-[:HAS_VARIETY]->(v:Variety)
            RETURN s.name AS name, s.world_share AS share, s.characteristics AS char,
                   s.altitude_range AS alt, s.temperature AS temp, s.rainfall AS rain,
                   s.origin AS origin, collect(DISTINCT v.name) AS varieties
            """
            sp_data = session.run(q_species).data()
            for sp in sp_data:
                vars_str = ', '.join(sp['varieties']) if sp['varieties'] else 'N/A'
                graph_facts.append(
                    f"[สายพันธุ์: {sp['name']}] สัดส่วนในโลก: {sp['share']} | แหล่งกำเนิด: {sp['origin']}\n"
                    f"  - ลักษณะ: {sp['char']}\n"
                    f"  - สภาพแวดล้อม: ความสูง {sp['alt']}, อุณหภูมิ {sp['temp']}, ปริมาณน้ำฝน {sp['rain']}\n"
                    f"  - สายพันธุ์ย่อย: {vars_str}"
                )

        # 4. Latte Art & Steaming Match
        if any(w in question for w in ['ลาเต้อาร์ต', 'สตรีมนม', 'โฟมนม', 'นม', 'เทนม', 'latte art', 'microfoam', 'วาด']):
            q_la = """
            MATCH (la:LatteArt)
            OPTIONAL MATCH (la)-[:HAS_TECHNIQUE]->(t:LatteArtTechnique)
            RETURN la.origin AS origin, la.steaming_temp AS temp, la.science AS science,
                   collect(DISTINCT t.name + ' (' + t.description + ')') AS techniques
            """
            la_data = session.run(q_la).data()
            for la in la_data:
                tech_str = ' | '.join(la['techniques'])
                graph_facts.append(
                    f"[ลาเต้อาร์ตและโฟมนม] ต้นกำเนิด: {la['origin']} | อุณหภูมิสตีมที่เหมาะสม: {la['temp']}\n"
                    f"  - หลักการทางวิทยาศาสตร์: {la['science']}\n"
                    f"  - เทคนิค: {tech_str}"
                )

        # 5. General Entity Relations Match
        q_gen = """
        MATCH (s:Entity)-[r]->(t:Entity)
        WHERE any(w IN $tokens WHERE s.name CONTAINS w OR t.name CONTAINS w)
        RETURN s.name AS source, type(r) AS rel, t.name AS target
        LIMIT 10
        """
        gen_data = session.run(q_gen, {"tokens": tokens}).data()
        for g in gen_data:
            graph_facts.append(f"- ({g['source']}) --[{g['rel']}]--> ({g['target']})")

    if not graph_facts:
        return "ไม่พบข้อมูลความสัมพันธ์ใน Graph โดยตรง"
    return "\n\n".join(graph_facts[:10])

# ============================================================
# 4. HYBRID GENERATION (WITH CHAT HISTORY)
# ============================================================

def llm_response(question: str, chat_history: str = "") -> str:
    """
    Hybrid RAG generation combining Vector Search, BM25, and Neo4j Graph traversal.
    """
    retrieved_docs = hybrid_search_documents(question, top_k=TOP_K)
    graph_context = search_graph_context(question)

    if retrieved_docs:
        vector_context = "\n\n".join([
            f"[หน้า {d.metadata.get('pages', 'N/A')}]\n{d.page_content}"
            for d in retrieved_docs
        ])
    else:
        vector_context = "ไม่พบข้อมูลใน Vector Store"

    history_str = chat_history.strip() if chat_history and chat_history.strip() else "ไม่มีประวัติการสนทนาก่อนหน้า"

    prompt = f"""คุณคือ SmartDoc Assistant ผู้ช่วยอัจฉริยะด้านการชงกาแฟและหลักสูตรบาริสต้ามืออาชีพ จากคู่มือการฝึกอบรม (documents.pdf)

กฎการตอบ:
1. วิเคราะห์คำถามปัจจุบันร่วมกับ [ประวัติการสนทนาที่ผ่านมา] โดยเฉพาะคำถามต่อเนื่องหรือสรรพนาม (มัน, เมนูนี้, สายพันธุ์ดังกล่าว)
2. นำข้อมูลจาก [บริบทจากกราฟความสัมพันธ์ Neo4j] และ [บริบทจากเอกสาร PDF] มาตอบให้ครบถ้วน ถูกต้อง แม่นยำ ตรงตามสูตรและหลักวิชาการ
3. หากถามสูตรกาแฟ ให้แจกแจง วัตถุดิบ (พร้อมสัดส่วน เช่น ออนซ์/มล./กรัม), อุปกรณ์, ขั้นตอนการทำอย่างเป็นลำดับข้อ และเคล็ดลับบาริสต้า
4. หากถามปัญหาการชง (เช่น กาแฟเปรี้ยว ขม ครีมม่าบาง) ให้อธิบายสาเหตุที่แท้จริงและวิธีแก้ไขอย่างชัดเจน
5. หากข้อมูลไม่มีในเอกสาร ให้ตอบอย่างสุภาพว่า "ไม่พบข้อมูลดังกล่าวในคู่มือบาริสต้ามืออาชีพครับ"
6. ตอบเป็นภาษาไทยที่สุภาพ เป็นมิตร กระชับ และจัดรูปแบบด้วย Markdown ให้อ่านง่าย

[ประวัติการสนทนาที่ผ่านมา]:
{history_str}

[บริบทจากเอกสาร PDF]:
{vector_context}

[บริบทจากกราฟความสัมพันธ์ Neo4j]:
{graph_context}

คำถามปัจจุบัน: {question}
คำตอบ:"""

    # 1. Generate via local Ollama LLM
    if llm:
        try:
            resp = llm.invoke(prompt)
            return resp.content.strip()
        except Exception as e:
            print(f"Ollama execution warning: {e}")

    # 2. Dynamic synthesis fallback directly from retrieved contexts
    output_parts = ["📋 **ข้อมูลจากคู่มือบาริสต้าและ Knowledge Graph:**\n"]
    if graph_context and "ไม่พบข้อมูลความสัมพันธ์" not in graph_context:
        output_parts.append(f"**ความสัมพันธ์และข้อมูลเฉพาะจาก Graph:**\n{graph_context}\n")
    if retrieved_docs:
        output_parts.append(f"**เนื้อหาที่เกี่ยวข้องจากเอกสาร:**\n{vector_context[:500]}...")
    return "\n".join(output_parts)

if __name__ == "__main__":
    print("=" * 65)
    print("🧪 TESTING RAG SEARCH WITH COFFEE KNOWLEDGE GRAPH")
    print("=" * 65)
    
    test_q = "ขอสูตรกาแฟส้มหน่อย ใช้วัตถุดิบและอุปกรณ์อะไรบ้าง และทำอย่างไร"
    print(f"\n❓ [Question]: {test_q}")
    ans = llm_response(test_q)
    print(f"🤖 [Answer]:\n{ans}\n" + "=" * 65)
