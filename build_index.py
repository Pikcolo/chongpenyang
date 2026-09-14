import os
import sys
from dotenv import load_dotenv
from pypdf import PdfReader
from langchain_core.documents import Document
from langchain_huggingface import HuggingFaceEmbeddings
from langchain_community.vectorstores import FAISS

# Prevent Unicode display errors in Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

PDF_PATH = os.getenv("PDF_PATH", "documents.pdf")
FAISS_PATH = os.getenv("FAISS_PATH", "faiss_index")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")

def clean_thai_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace('\ufffd', 'า')
    text = text.replace('กำแฟ', 'กาแฟ')
    text = text.replace('ลำเต้', 'ลาเต้')
    text = text.replace('อเมริกำโน่', 'อเมริกาโน่')
    text = text.replace('น ้ำ', 'น้ำ')
    text = text.replace('น ้าร้อน', 'น้ำร้อน')
    text = text.replace('น ้าผึ้ง', 'น้ำผึ้ง')
    text = text.replace('น ้ามะนาว', 'น้ำมะนาว')
    text = text.replace('น ้าส้ม', 'น้ำส้ม')
    text = text.replace('น ้าสัม', 'น้ำส้ม')
    text = text.replace('น ้าแข็ง', 'น้ำแข็ง')
    text = text.replace('น ้าตาล', 'น้ำตาล')
    text = text.replace('น ้ามัน', 'น้ำมัน')
    text = text.replace('น ้าเชื่อม', 'น้ำเชื่อม')
    text = text.replace('น ้าเย็น', 'น้ำเย็น')
    text = text.replace('น ้าอุ่น', 'น้ำอุ่น')
    text = text.replace('ถวงตวง', 'ถ้วยตวง')
    text = text.replace('ใส้ก้านชง', 'ใส่ก้านชง')
    text = text.replace('แทมปักาแฟ', 'แทมป์กาแฟ')
    text = text.replace('ซ้อนตักกาแฟ', 'ช้อนตักกาแฟ')
    text = text.replace('สกัดช็อค', 'สกัดช็อต')
    text = text.replace('เรอสกัด', 'รอสกัด')
    text = text.replace('เอสเพรสโช่', 'เอสเพรสโซ่')
    text = text.replace('เอสเพรสโช', 'เอสเพรสโซ่')
    text = text.replace('เฮสเปรสโซ่', 'เอสเพรสโซ่')
    return text

def extract_chunks_from_pdf(path, chunk_size=20, overlap=6):
    print(f"📖 Extracting text from '{path}'...")
    reader = PdfReader(path)
    lines = []
    for page_no, page in enumerate(reader.pages, start=1):
        raw = page.extract_text() or ""
        cleaned = clean_thai_text(raw)
        for line in cleaned.split("\n"):
            line = line.strip()
            if line and len(line) > 2:
                # filter repetitive headers
                if any(k in line for k in ['ใบข้อมูล', 'หลักสูตร  :บาริสต้ามืออาชีพ', 'หัวข้อวิชา', 'งานย่อยที่', 'เวลา 1 ชั่วโมง', 'เวลา 5 ชั่วโมง']):
                    continue
                lines.append({"text": line, "page": page_no})

    chunks = []
    step = chunk_size - overlap
    for i in range(0, len(lines), step):
        selected = lines[i:i + chunk_size]
        if not selected:
            continue
        text = "\n".join(item["text"] for item in selected)
        pages = sorted(set(item["page"] for item in selected))
        chunks.append(
            Document(
                page_content=text,
                metadata={"start_line": i, "pages": pages, "chunk_id": len(chunks)}
            )
        )
    print(f"✅ Created {len(chunks)} text chunks across {len(reader.pages)} pages.")
    return chunks

def build_vector_index():
    print("=" * 65)
    print("🧠 BUILDING FAISS VECTOR INDEX FOR HYBRID RAG")
    print("=" * 65)
    
    chunks = extract_chunks_from_pdf(PDF_PATH, chunk_size=20, overlap=6)
    
    print(f"Loading embedding model: '{EMBED_MODEL}'...")
    embeddings = HuggingFaceEmbeddings(
        model_name=EMBED_MODEL,
        model_kwargs={'device': 'cpu'}
    )
    
    print("Vectorizing chunks with FAISS...")
    vectorstore = FAISS.from_documents(chunks, embeddings)
    
    os.makedirs(FAISS_PATH, exist_ok=True)
    vectorstore.save_local(FAISS_PATH)
    print(f"✅ FAISS index successfully built and saved to '{FAISS_PATH}'!")

if __name__ == "__main__":
    build_vector_index()
