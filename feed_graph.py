import os
import sys
import json
import argparse
from typing import Optional, List

from dotenv import load_dotenv
import pymupdf  # PyMuPDF / fitz
from pydantic import BaseModel, Field
import torch
from sentence_transformers import SentenceTransformer, util
from neo4j import GraphDatabase

# Prevent Unicode display errors in Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

# ============================================================
# 1. LOAD ENVIRONMENT VARIABLES (SECURE VALIDATION)
# ============================================================

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

if not NEO4J_URI or not NEO4J_USER or not NEO4J_PASSWORD:
    raise ValueError(
        "❌ [Security Error] ไม่พบการกำหนดค่าความปลอดภัยสำหรับเชื่อมต่อ Neo4j ในไฟล์ .env\n"
        "   กรุณากำหนด NEO4J_URI, NEO4J_USER และ NEO4J_PASSWORD ให้ครบถ้วนในไฟล์ .env"
    )

PDF_PATH = os.getenv("PDF_PATH", "documents.pdf")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:7b")
EMBED_MODEL = os.getenv("EMBED_MODEL", "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2")
JSON_OUTPUT_PATH = os.getenv("PAGE_KNOWLEDGE_PATH", "page_knowledge.json")


# ============================================================
# 2. DOMAIN ONTOLOGY (หลักสูตร: บาริสต้ามืออาชีพ)
# ============================================================

COFFEE_ONTOLOGY = {
    "Species": [
        "กาแฟอาราบิก้า", "อาราบิก้า", "Coffea Arabica",
        "กาแฟโรบัสต้า", "โรบัสต้า", "Coffea Canephora",
        "กาแฟพีเบอร์รี่", "พีเบอร์รี่", "Peaberry"
    ],
    "Variety": [
        "Typica", "Bourbon", "Caturra", "Mundo Novo", "Tico",
        "San Ramon", "Jamaica Blue Mountain", "Catimor", "Geisha"
    ],
    "ProductionStep": [
        "การปลูก", "การเก็บเกี่ยว", "การแปรรูป", "Dry Method", "Wet Method",
        "การสีคัดแยก", "Cupping", "การคั่วกาแฟ", "การบดกาแฟ", "การชงกาแฟ"
    ],
    "RoastLevel": [
        "คั่วอ่อน", "Light Roast", "Agtron 70",
        "คั่วกลาง", "Medium Roast", "Agtron 50-69",
        "คั่วเข้ม", "Dark Roast", "French Roast", "Agtron น้อยกว่า 50"
    ],
    "GrindSize": [
        "ละเอียดมาก", "Extra Fine",
        "ละเอียด", "Fine",
        "ค่อนข้างละเอียด", "Medium Fine",
        "ปานกลาง", "Medium",
        "หยาบ", "Coarse"
    ],
    "ExtractionStatus": [
        "Espresso Perfect", "การสกัดที่สมบูรณ์แบบ",
        "Under Extraction", "สกัดน้อยเกินไป",
        "Over Extraction", "สกัดมากเกินไป"
    ],
    "ExtractionCause": [
        "บดกาแฟหยาบเกินไป", "บดกาแฟละเอียดเกินไป",
        "แทมป์เบาเกินไป", "แทมป์แน่นเกินไป",
        "ปริมาณผงกาแฟน้อยเกินไป", "ปริมาณผงกาแฟมากเกินไป",
        "อุณหภูมิน้ำต่ำกว่า 88°C", "อุณหภูมิน้ำสูงเกิน 95°C",
        "เวลาการสกัดสั้นเกินไป", "เวลาการสกัดนานเกินไป"
    ],
    "ExtractionSolution": [
        "ปรับเบอร์บดให้ละเอียดขึ้น", "ปรับเบอร์บดให้หยาบขึ้น",
        "เพิ่มปริมาณผงกาแฟ", "ลดปริมาณผงกาแฟ",
        "แทมป์ให้แน่นและระนาบตรง", "แทมป์ด้วยแรงพอดี",
        "ปรับอุณหภูมิน้ำให้อยู่ในช่วง 88-95°C"
    ],
    "LatteArt": [
        "ลาเต้อาร์ต", "Latte Art", "Microfoam", "ไมโครโฟม", "การสตรีมนม", "อุณหภูมิ 60-65°C"
    ],
    "LatteArtTechnique": [
        "Free Pour", "การเทอิสระ", "Etching", "การวาดลาย",
        "ลายหัวใจ", "ลายทิวลิป", "ลายโรเซ็ตต้า"
    ],
    "Beverage": [
        "เอสเพรสโซ่ร้อน", "อเมริกาโน่ร้อน", "ลาเต้ร้อน", "คาปูชิโน่ร้อน", "มอคค่าร้อน",
        "เอสเพรสโซ่เย็น สไตล์ไทย", "อเมริกาโน่เย็น", "ลาเต้เย็น", "คาปูชิโน่เย็น",
        "กาแฟส้ม", "กาแฟพีช", "กาแฟมะนาว", "ลาเต้มิ้นท์"
    ],
    "Ingredient": [
        "เมล็ดกาแฟ", "เอสเพรสโซ่ช็อต", "นมสด", "นมข้นหวาน", "นมข้นจืด",
        "น้ำส้ม", "น้ำผึ้ง", "น้ำเชื่อม", "น้ำมะนาว", "ไซรัปพีช", "ไซรัปมิ้นท์",
        "ผงชินนาม่อน", "ผงโกโก้", "น้ำแข็ง"
    ],
    "Equipment": [
        "เครื่องชง Espresso", "เครื่องบดกาแฟ", "ก้านชง", "Portafilter",
        "แทมเปอร์", "Tamper", "พิตเชอร์", "Pitcher", "Moka Pot", "แก้วช็อต", "เทอร์โมมิเตอร์"
    ]
}

ALLOWED_RELATIONS = [
    "HAS_VARIETY",
    "PRECEDES",
    "PRODUCES",
    "DETERMINES",
    "REQUIRES_ROAST",
    "RECOMMENDS_GRIND",
    "USES_INGREDIENT",
    "USES_EQUIPMENT",
    "HAS_STEP",
    "NEXT_STEP",
    "STRIVES_FOR",
    "CAUSED_BY",
    "RESOLVED_BY",
    "HAS_TECHNIQUE",
    "APPLIES_TECHNIQUE",
    "BREWED_WITH",
    "DESCRIBES_RECIPE",
    "COVERS_PAGE",
    "HAS_MODULE",
    "HAS_KEYWORD",
    "MENTIONS",
    "HAS_QUIZ"
]

# ============================================================
# 3. PYDANTIC SCHEMA
# ============================================================

class Entity(BaseModel):
    name: str = Field(description="ชื่อ Entity หรือคำสำคัญเฉพาะทางด้านกาแฟ")
    type: str = Field(description="ประเภท Entity ตาม Coffee Ontology")
    description: Optional[str] = Field(default=None, description="รายละเอียดเพิ่มเติม (ถ้ามี)")

class Relation(BaseModel):
    source: str = Field(description="ชื่อ Entity ต้นทาง")
    relation: str = Field(description="ประเภทความสัมพันธ์ (ต้องอยู่ใน ALLOWED_RELATIONS)")
    target: str = Field(description="ชื่อ Entity ปลายทาง")

class PageKnowledge(BaseModel):
    summary: str = Field(description="สรุปองค์ความรู้สำคัญของหน้านี้ 1-3 บรรทัด")
    entities: List[Entity] = Field(default_factory=list)
    relations: List[Relation] = Field(default_factory=list)

# ============================================================
# 4. SBERT VECTORIZED KEYWORD EXTRACTOR (TOP-K SALIENT FILTER)
# ============================================================

class SbertKeywordMatcher:
    def __init__(self, model_name: str, ontology: dict):
        print(f"🧠 Loading SBERT Model: '{model_name}'...")
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = SentenceTransformer(model_name, device=self.device)
        
        self.ontology_terms = []
        self.ontology_types = []
        for entity_type, terms in ontology.items():
            for term in terms:
                self.ontology_terms.append(term)
                self.ontology_types.append(entity_type)
        
        print(f"⚡ Pre-encoding {len(self.ontology_terms)} Ontology terms...")
        self.ontology_embeddings = self.model.encode(
            self.ontology_terms,
            convert_to_tensor=True,
            show_progress_bar=False,
            device=self.device
        )
        print("✅ SBERT initialized successfully.")

    def extract_keywords(self, text: str, threshold: float = 0.58, top_k: int = 5) -> List[dict]:
        """
        Matrix Cosine Similarity with Salient Top-K Filter to prevent relationship bloating.
        """
        sentences = [s.strip() for s in text.split("\n") if len(s.strip()) > 3]
        if not sentences:
            return []
        
        sentence_embeddings = self.model.encode(
            sentences,
            convert_to_tensor=True,
            show_progress_bar=False,
            device=self.device
        )
        
        sim_matrix = util.cos_sim(sentence_embeddings, self.ontology_embeddings)
        
        matched_dict = {}
        for s_idx in range(len(sentences)):
            row = sim_matrix[s_idx]
            matches = torch.nonzero(row >= threshold).squeeze(1)
            for m_idx in matches:
                idx = int(m_idx)
                score = round(float(row[idx]), 4)
                term = self.ontology_terms[idx]
                e_type = self.ontology_types[idx]
                key = (term, e_type)
                if key not in matched_dict or score > matched_dict[key]["score"]:
                    matched_dict[key] = {
                        "keyword": term,
                        "type": e_type,
                        "score": score
                    }
        
        # Sort by score and take ONLY top_k salient keywords
        sorted_kws = sorted(list(matched_dict.values()), key=lambda x: x["score"], reverse=True)
        return sorted_kws[:top_k]

# ============================================================
# 5. TEXT EXTRACTION & NORMALIZATION
# ============================================================

def clean_thai_text(text: str) -> str:
    if not text:
        return ""
    text = text.replace('\ufffd', 'า')
    text = text.replace('กำแฟ', 'กาแฟ').replace('ลำเต้', 'ลาเต้')
    text = text.replace('อเมริกำโน่', 'อเมริกาโน่').replace('เอสเพรสโช', 'เอสเพรสโซ่')
    text = text.replace('น ้ำ', 'น้ำ').replace('น ้าร้อน', 'น้ำร้อน').replace('น ้าส้ม', 'น้ำส้ม')
    text = text.replace('น ้าแข็ง', 'น้ำแข็ง').replace('น ้าเชื่อม', 'น้ำเชื่อม')
    text = text.replace('แทมปักาแฟ', 'แทมป์กาแฟ').replace('สกัดช็อค', 'สกัดช็อต')
    return text.strip()

def extract_pages_from_pdf(pdf_path: str):
    if not os.path.exists(pdf_path):
        print(f"❌ ไม่พบไฟล์ PDF: {pdf_path}")
        return []
    doc = pymupdf.open(pdf_path)
    pages = []
    for idx, page in enumerate(doc):
        raw = page.get_text("text") or ""
        cleaned = clean_thai_text(raw)
        pages.append({
            "page": idx + 1,
            "raw_text": cleaned
        })
    doc.close()
    return pages

# ============================================================
# 6. CURATED DOMAIN KNOWLEDGE BASE (13 RECIPES, 10 STEPS, ETC.)
# ============================================================

def get_curated_knowledge():
    return {
        "modules": [
            {"id": "MOD_01", "name": "ความรู้เบื้องต้นเกี่ยวกับเมล็ดกาแฟ", "page_start": 3, "page_end": 19},
            {"id": "MOD_02", "name": "เคล็ดลับการชงกาแฟ หลักการและวิธีการ", "page_start": 20, "page_end": 31},
            {"id": "MOD_03", "name": "ประวัติความเป็นมาและศาสตร์ของลาเต้อาร์ต", "page_start": 32, "page_end": 36},
            {"id": "MOD_04", "name": "ใบขั้นตอนการปฏิบัติงาน การชงเครื่องดื่มกาแฟร้อนและเย็น", "page_start": 37, "page_end": 50},
            {"id": "MOD_05", "name": "ใบงาน ใบทดสอบ และใบเฉลย", "page_start": 51, "page_end": 53}
        ],
        "species": [
            {
                "name": "กาแฟอาราบิก้า (Coffea Arabica)",
                "world_share": "ประมาณ 70%",
                "varieties": ["Typica", "Bourbon", "Caturra", "Mundo Novo", "Tico", "San Ramon", "Jamaica Blue Mountain"]
            },
            {
                "name": "กาแฟโรบัสต้า (Coffea Canephora)",
                "world_share": "ประมาณ 30%",
                "varieties": ["Robusta Standard"]
            },
            {
                "name": "พีเบอร์รี่ (Peaberry)",
                "world_share": "ประมาณ 5%",
                "varieties": ["Peaberry Arabica"]
            }
        ],
        "production_steps": [
            {"step": 1, "name": "การปลูก (Planting)"},
            {"step": 2, "name": "การเก็บเกี่ยว (Harvesting)"},
            {"step": 3, "name": "การแปรรูป (Processing)"},
            {"step": 4, "name": "การสีคัดแยก (Milling & Sorting)"},
            {"step": 5, "name": "การทดสอบคุณภาพ (Cupping)"},
            {"step": 6, "name": "การคั่วกาแฟ (Roasting)"},
            {"step": 7, "name": "การบดกาแฟ (Grinding)"},
            {"step": 8, "name": "การชงกาแฟ (Brewing)"},
            {"step": 9, "name": "การดื่มอย่างมีความสุข (Tasting & Enjoying)"},
            {"step": 10, "name": "ศาสตร์และศิลป์บาริสต้า (Barista Craft & Art)"}
        ],
        "roast_levels": [
            {"name": "คั่วอ่อน (Light Roast)", "agtron": "70 ขึ้นไป"},
            {"name": "คั่วกลาง (Medium Roast)", "agtron": "50 - 69"},
            {"name": "คั่วเข้ม (Dark Roast / French Roast)", "agtron": "น้อยกว่า 50"}
        ],
        "grind_sizes": [
            {"name": "ละเอียดมาก (Extra Fine)", "eq": "Turkish Coffee"},
            {"name": "ละเอียด (Fine)", "eq": "เครื่องชง Espresso"},
            {"name": "ค่อนข้างละเอียด (Medium Fine)", "eq": "Moka Pot"},
            {"name": "ปานกลาง (Medium)", "eq": "Drip / Pour Over"},
            {"name": "หยาบ (Coarse)", "eq": "French Press"}
        ],
        "extraction_statuses": [
            {
                "status": "Espresso Perfect (Good Extraction)",
                "crema": "สีน้ำตาลทอง หนาเนียน",
                "taste": "รสชาติกลมกล่อม มีความหวานฉ่ำ สมดุล",
                "causes": "บดกาแฟได้ขนาดพอดี แทมป์แรงสม่ำเสมอ อุณหภูมิน้ำ 88-95°C",
                "solutions": "รักษามาตรฐานการบด แทมป์ และอุณหภูมิเครื่องชงให้คงที่"
            },
            {
                "status": "Under Extraction (สกัดน้อยเกินไป)",
                "crema": "สีอ่อน ครีมม่าบาง ละลายเร็ว",
                "taste": "รสเปรี้ยวโดด ฝาดเฝื่อน เค็ม ขาดความหวาน",
                "causes": "บดกาแฟหยาบเกินไป, แทมป์เบาเกินไป, ผงกาแฟน้อนเกินไป, น้ำต่ำกว่า 88°C",
                "solutions": "ปรับเบอร์บดให้ละเอียดขึ้น, เพิ่มปริมาณผงกาแฟ, แทมป์ให้แน่นสม่ำเสมอ, เพิ่มอุณหภูมิน้ำ"
            },
            {
                "status": "Over Extraction (สกัดมากเกินไป)",
                "crema": "สีน้ำตาลเข้มจัดจนดำ ครีมม่าหยาบ",
                "taste": "รสขมจัด ขมไหม้ แห้งฝาดติดคอ มีกลิ่นควัน",
                "causes": "บดกาแฟละเอียดเกินไป, แทมป์แน่นเกินไป, ผงกาแฟมากเกินไป, น้ำเกิน 95°C",
                "solutions": "ปรับเบอร์บดให้หยาบขึ้นเล็กน้อย, แทมป์แรงพอดีมือ, ปรับลดอุณหภูมิน้ำ"
            }
        ],
        "latte_art": {
            "name": "ศาสตร์แห่งลาเต้อาร์ต",
            "temp": "60 - 65 องศาเซลเซียส",
            "techniques": [
                {"name": "Free Pour (การเทอิสระ)", "patterns": ["หัวใจ", "ทิวลิป", "โรเซ็ตต้า"]},
                {"name": "Etching (การลากลาย / การวาดลาย)", "patterns": ["ลายสัตว์", "ใยแมงมุม"]}
            ]
        },
        "beverages": [
            {
                "name": "เอสเพรสโซ่ร้อน (Hot Espresso)",
                "category": "Hot Coffee", "page": 39,
                "roast": "คั่วกลาง หรือ คั่วเข้ม", "grind": "ละเอียด (Fine)",
                "ingredients": [{"name": "เมล็ดกาแฟดอยไทยคั่วกลางหรือคั่วเข้ม", "amount": "15-18", "unit": "กรัม"}],
                "equipment": ["เครื่องชง Espresso", "เครื่องบดกาแฟ", "ก้านชง (Portafilter)", "แทมเปอร์ (Tamper)", "แก้วช็อต (Shot Glass)"],
                "steps": [
                    {"step": 1, "action": "ตวงกาแฟ 15-18 กรัม และบดให้ละเอียด"},
                    {"step": 2, "action": "ใส่ผงกาแฟลงในก้านชง เกลี่ยให้เรียบ แล้วแทมป์ให้แน่นพอตึงมือ"},
                    {"step": 3, "action": "ใส่ก้านชงเข้าหัวกรุ๊ป กดสกัดช็อต 25-30 วินาที ได้น้ำกาแฟ 1-2 ออนซ์"}
                ]
            },
            {
                "name": "อเมริกาโน่ร้อน (Hot Americano)",
                "category": "Hot Coffee", "page": 40,
                "roast": "คั่วกลาง หรือ คั่วเข้ม", "grind": "ละเอียด (Fine)",
                "ingredients": [
                    {"name": "เอสเพรสโซ่ช็อต", "amount": "1-2", "unit": "ช็อต"},
                    {"name": "น้ำร้อน", "amount": "4-6", "unit": "ออนซ์"}
                ],
                "equipment": ["เครื่องชง Espresso", "กาต้มน้ำร้อน / หัวจ่ายน้ำร้อน", "แก้วร้อน"],
                "steps": [
                    {"step": 1, "action": "สกัดกาแฟเอสเพรสโซ่ 1-2 ช็อต"},
                    {"step": 2, "action": "เทน้ำร้อน 4-6 ออนซ์ลงในแก้ว"},
                    {"step": 3, "action": "เทช็อตเอสเพรสโซ่ผสมลงไปในน้ำร้อน พร้อมเสิร์ฟ"}
                ]
            },
            {
                "name": "ลาเต้ร้อน (Hot Latte)",
                "category": "Hot Coffee", "page": 40,
                "roast": "คั่วกลางค่อนเข้ม", "grind": "ละเอียด (Fine)",
                "ingredients": [
                    {"name": "เอสเพรสโซ่ช็อต", "amount": "1", "unit": "ช็อต"},
                    {"name": "นมสดสตรีมร้อน", "amount": "2/3", "unit": "ส่วน"},
                    {"name": "โฟมนมเนียนละเอียด", "amount": "1", "unit": "ซม."}
                ],
                "equipment": ["เครื่องชง Espresso", "พิตเชอร์สตรีมนม", "เทอร์โมมิเตอร์", "แก้วลาเต้"],
                "steps": [
                    {"step": 1, "action": "สกัดเอสเพรสโซ่ 1 ช็อตใส่แก้วเสิร์ฟ"},
                    {"step": 2, "action": "สตรีมนมสดให้ได้อุณหภูมิ 60-65°C และได้ไมโครโฟมเนียนละเอียด"},
                    {"step": 3, "action": "เทนมร้อนผสมกับกาแฟ และเทโฟมนมปิดท้าย หนาประมาณ 1 ซม. หรือเทเป็นลายลาเต้อาร์ต"}
                ]
            },
            {
                "name": "คาปูชิโน่ร้อน (Hot Cappuccino)",
                "category": "Hot Coffee", "page": 40,
                "roast": "คั่วกลางค่อนเข้ม หรือ คั่วเข้ม", "grind": "ละเอียด (Fine)",
                "ingredients": [
                    {"name": "เอสเพรสโซ่ช็อต", "amount": "1/3", "unit": "ส่วน"},
                    {"name": "นมสดสตรีมร้อน", "amount": "1/3", "unit": "ส่วน"},
                    {"name": "โฟมนมหนานุ่ม", "amount": "1/3", "unit": "ส่วน"},
                    {"name": "ผงชินนาม่อน", "amount": "เล็กน้อย", "unit": "โรยหน้า"}
                ],
                "equipment": ["เครื่องชง Espresso", "พิตเชอร์สตรีมนม", "แก้วคาปูชิโน่", "กระบอกโรยผงชินนาม่อน"],
                "steps": [
                    {"step": 1, "action": "สกัดเอสเพรสโซ่ 1 ช็อตใส่แก้วคาปูชิโน่"},
                    {"step": 2, "action": "สตรีมนมโดยดึงอากาศเข้ามากกว่าลาเต้ เพื่อให้ได้โฟมนมหนานุ่มฟู"},
                    {"step": 3, "action": "เทนมสตรีมลงไป 1/3 ส่วน และตักหรือเทโฟมนมหนา 1/3 ส่วน"},
                    {"step": 4, "action": "โรยผงชินนาม่อนด้านบนเพื่อเพิ่มความหอม"}
                ]
            },
            {
                "name": "มอคค่าร้อน (Hot Mocha)",
                "category": "Hot Coffee", "page": 41,
                "roast": "คั่วเข้ม", "grind": "ละเอียด (Fine)",
                "ingredients": [
                    {"name": "เอสเพรสโซ่ช็อต", "amount": "1", "unit": "ช็อต"},
                    {"name": "ผงโกโก้หรือซอสช็อกโกแลต", "amount": "1-2", "unit": "ช้อนโต๊ะ"},
                    {"name": "นมสดสตรีมร้อน", "amount": "1/2", "unit": "แก้ว"},
                    {"name": "วิปปิ้งครีม", "amount": "พอประมาณ", "unit": "บีบด้านบน"}
                ],
                "equipment": ["เครื่องชง Espresso", "พิตเชอร์สตรีมนม", "แก้วร้อน", "ช้อนคน"],
                "steps": [
                    {"step": 1, "action": "ผสมผงโกโก้หรือซอสช็อกโกแลตกับเอสเพรสโซ่ร้อน คนให้ละลายเข้ากันดี"},
                    {"step": 2, "action": "สตรีมนมสดให้ร้อน 60-65°C แล้วเทผสมลงในแก้วกาแฟช็อกโกแลต"},
                    {"step": 3, "action": "ตกแต่งด้านบนด้วยโฟมนมหรือวิปครีม และราดซอสช็อกโกแลต พร้อมเสิร์ฟ"}
                ]
            },
            {
                "name": "กาแฟส้ม (Orange Coffee / Espresso Orange)",
                "category": "Cold Coffee", "page": 45,
                "roast": "เมล็ดกาแฟดอยไทย คละเมล็ดคั่วกลาง", "grind": "ค่อนไปทางละเอียด ประมาณน้ำตาลทราย",
                "ingredients": [
                    {"name": "เมล็ดกาแฟดอยไทย คละเมล็ดคั่วกลาง", "amount": "15-18", "unit": "กรัม"},
                    {"name": "น้ำส้มแท้", "amount": "6", "unit": "ออนซ์ (180 ml)"},
                    {"name": "น้ำแข็ง", "amount": "เต็มแก้ว", "unit": "แก้ว"}
                ],
                "equipment": ["เครื่อง Espresso เล็ก", "เครื่องบดกาแฟ", "ช้อนตักกาแฟ และเครื่องชั่งดิจิตอล", "ถ้วยตวง", "กาต้มน้ำร้อน"],
                "steps": [
                    {"step": 1, "action": "ตวงเมล็ดกาแฟ 15 กรัม ใส่เครื่องบด บดค่อนไปทางละเอียด ประมาณน้ำตาลทราย"},
                    {"step": 2, "action": "เปิดเครื่อง Espresso วอร์มเครื่องรอ"},
                    {"step": 3, "action": "เทผงกาแฟใส่ก้านชง แล้ว Tamp ให้แน่นและเนียนเรียบเท่ากัน"},
                    {"step": 4, "action": "สกัดช็อตกาแฟออกมา 2-6 ออนซ์"},
                    {"step": 5, "action": "ตักน้ำแข็งให้เต็มแก้ว ใส่น้ำส้มลงไป 6 ออนซ์"},
                    {"step": 6, "action": "ค่อยๆ เทกาแฟที่สกัดได้ลงด้านบนอย่างเบามือ ให้แยกชั้นสวยงาม"}
                ]
            },
            {
                "name": "กาแฟพีช (Peach Coffee / Moka Pot Peach)",
                "category": "Cold Coffee", "page": 46,
                "roast": "คั่วกลางค่อนเข้ม", "grind": "ค่อนข้างละเอียด (15 คลิก สำหรับ Moka Pot)",
                "ingredients": [
                    {"name": "เมล็ดกาแฟคั่วกลางค่อนเข้ม", "amount": "15-18", "unit": "กรัม"},
                    {"name": "ไซรัปพีช", "amount": "30", "unit": "ml"},
                    {"name": "น้ำเปล่าหรือโซดา", "amount": "90", "unit": "ml"},
                    {"name": "น้ำแข็ง", "amount": "เต็มแก้ว", "unit": "แก้ว"}
                ],
                "equipment": ["Moka Pot 3 cup", "เตาไฟฟ้าหรือเตาแก๊สปิคนิค", "เครื่องบดมือหมุน", "ถ้วยตวง", "แก้วเสิร์ฟ"],
                "steps": [
                    {"step": 1, "action": "บดเมล็ดกาแฟ 15 กรัม เบอร์ 15 คลิก สำหรับ Moka Pot"},
                    {"step": 2, "action": "ใส่น้ำอุ่นในหม้อต้ม Moka Pot ด้านล่าง ไม่เกินวาล์วความปลอดภัย"},
                    {"step": 3, "action": "ใส่ผงกาแฟลงในกรวย ปาดให้เรียบ หมุนประกอบหม้อต้มให้แน่น"},
                    {"step": 4, "action": "นำขึ้นตั้งเตาไฟปานกลางค่อนอ่อน รอจนน้ำกาแฟไหลพุ่งขึ้นมาด้านบนจนหมด"},
                    {"step": 5, "action": "ผสมไซรัปพีชกับน้ำหรือโซดาในแก้ว แล้วตักน้ำแข็งใส่เต็มแก้ว"},
                    {"step": 6, "action": "เทกาแฟ Moka Pot ด้านบน พร้อมตกแต่งด้วยชิ้นเนื้อพีช"}
                ]
            },
            {
                "name": "เอสเพรสโซ่เย็น สไตล์ไทย (Es-Yen / Thai Style Iced Espresso)",
                "category": "Cold Coffee", "page": 43,
                "roast": "คั่วเข้ม (Dark Roast)", "grind": "ละเอียด (Fine)",
                "ingredients": [
                    {"name": "เอสเพรสโซ่ช็อตเข้มข้น", "amount": "2", "unit": "ช็อต (60 ml)"},
                    {"name": "นมข้นหวาน", "amount": "30-45", "unit": "ml"},
                    {"name": "นมข้นจืด", "amount": "30-45", "unit": "ml"},
                    {"name": "นมสด", "amount": "30", "unit": "ml"},
                    {"name": "น้ำแข็ง", "amount": "เต็มแก้ว", "unit": "แก้ว"}
                ],
                "equipment": ["เครื่องชง Espresso", "แก้วผสมกาแฟ", "ช้อนคน", "แก้วเสิร์ฟ 16-22 ออนซ์"],
                "steps": [
                    {"step": 1, "action": "สกัดกาแฟเอสเพรสโซ่เข้มข้น 2 ช็อต (ดับเบิ้ลช็อต)"},
                    {"step": 2, "action": "เติมนมข้นหวาน นมข้นจืด และนมสดลงในน้ำกาแฟร้อน"},
                    {"step": 3, "action": "คนให้ส่วนผสมละลายเข้ากันอย่างทั่วถึง"},
                    {"step": 4, "action": "เทลงในแก้วที่มีน้ำแข็งเต็มแก้ว ราดนมข้นจืดปิดท้ายด้านบน พร้อมเสิร์ฟ"}
                ]
            },
            {
                "name": "อเมริกาโน่เย็น (Iced Americano)",
                "category": "Cold Coffee", "page": 44,
                "roast": "คั่วกลาง หรือ คั่วเข้ม", "grind": "ละเอียด (Fine)",
                "ingredients": [
                    {"name": "เอสเพรสโซ่ช็อต", "amount": "2", "unit": "ช็อต (60 ml)"},
                    {"name": "น้ำเย็น", "amount": "4-6", "unit": "ออนซ์"},
                    {"name": "น้ำแข็ง", "amount": "เต็มแก้ว", "unit": "แก้ว"}
                ],
                "equipment": ["เครื่องชง Espresso", "แก้วตวง", "แก้วเสิร์ฟ"],
                "steps": [
                    {"step": 1, "action": "สกัดกาแฟเอสเพรสโซ่ 2 ช็อต"},
                    {"step": 2, "action": "ใส่น้ำเย็นและน้ำแข็งลงในแก้วเสิร์ฟ"},
                    {"step": 3, "action": "เทช็อตเอสเพรสโซ่ลงบนน้ำแข็ง พร้อมเสิร์ฟ"}
                ]
            },
            {
                "name": "ลาเต้เย็น (Iced Latte)",
                "category": "Cold Coffee", "page": 44,
                "roast": "คั่วกลางค่อนเข้ม", "grind": "ละเอียด (Fine)",
                "ingredients": [
                    {"name": "เอสเพรสโซ่ช็อต", "amount": "1-2", "unit": "ช็อต"},
                    {"name": "นมสดเย็น", "amount": "4-5", "unit": "ออนซ์ (120-150 ml)"},
                    {"name": "น้ำเชื่อม", "amount": "15-20", "unit": "ml"},
                    {"name": "น้ำแข็ง", "amount": "เต็มแก้ว", "unit": "แก้ว"}
                ],
                "equipment": ["เครื่องชง Espresso", "แก้วตวง", "ช้อนคน", "แก้วเสิร์ฟ"],
                "steps": [
                    {"step": 1, "action": "ผสมนมสดเย็นกับน้ำเชื่อมในแก้ว คนให้เข้ากัน"},
                    {"step": 2, "action": "ตักน้ำแข็งใส่จนเต็มแก้ว"},
                    {"step": 3, "action": "สกัดเอสเพรสโซ่แล้วเทราดด้านบน เกิดเป็นเลเยอร์สองชั้นสวยงาม"}
                ]
            },
            {
                "name": "คาปูชิโน่เย็น (Iced Cappuccino)",
                "category": "Cold Coffee", "page": 44,
                "roast": "คั่วเข้ม", "grind": "ละเอียด (Fine)",
                "ingredients": [
                    {"name": "เอสเพรสโซ่ช็อต", "amount": "2", "unit": "ช็อต"},
                    {"name": "นมสดเย็นผสมนมข้นหวาน", "amount": "60", "unit": "ml"},
                    {"name": "โฟมนมเย็นเนียนนุ่ม", "amount": "เต็มขอบแก้ว", "unit": "ชั้นบน"},
                    {"name": "ผงโกโก้", "amount": "เล็กน้อย", "unit": "โรยหน้า"}
                ],
                "equipment": ["เครื่องชง Espresso", "เครื่องตีฟองนมเย็น", "แก้วเสิร์ฟ"],
                "steps": [
                    {"step": 1, "action": "ผสมเอสเพรสโซ่กับนมสดและนมข้นหวาน คนให้เข้ากันแล้วเทลงแก้วน้ำแข็ง"},
                    {"step": 2, "action": "ตีโฟมนมเย็นให้ขึ้นฟูเนียนแน่น"},
                    {"step": 3, "action": "ตักโฟมนมหนานุ่มโปะทับด้านบน และโรยด้วยผงโกโก้"}
                ]
            },
            {
                "name": "กาแฟมะนาว (Espresso Lemon / Lime Coffee)",
                "category": "Cold Coffee", "page": 47,
                "roast": "คั่วกลาง", "grind": "ละเอียด (Fine)",
                "ingredients": [
                    {"name": "เอสเพรสโซ่ช็อต", "amount": "1-2", "unit": "ช็อต"},
                    {"name": "น้ำมะนาวคั้นสด", "amount": "20-30", "unit": "ml"},
                    {"name": "น้ำผึ้งหรือน้ำเชื่อม", "amount": "30", "unit": "ml"},
                    {"name": "โซดา", "amount": "60", "unit": "ml"},
                    {"name": "น้ำแข็ง", "amount": "เต็มแก้ว", "unit": "แก้ว"}
                ],
                "equipment": ["เครื่องชง Espresso", "ถ้วยตวง", "ช้อนคน", "แก้วเสิร์ฟ"],
                "steps": [
                    {"step": 1, "action": "ผสมน้ำมะนาว น้ำผึ้ง และโซดา คนให้เข้ากันในแก้ว"},
                    {"step": 2, "action": "ใส่น้ำแข็งให้เต็มแก้ว"},
                    {"step": 3, "action": "สกัดช็อตเอสเพรสโซ่ราดด้านบน ตกแต่งด้วยมะนาวฝาน"}
                ]
            },
            {
                "name": "ลาเต้มิ้นท์เย็น (Iced Mint Latte)",
                "category": "Cold Coffee", "page": 48,
                "roast": "คั่วกลางค่อนเข้ม", "grind": "ละเอียด (Fine)",
                "ingredients": [
                    {"name": "เอสเพรสโซ่ช็อต", "amount": "1-2", "unit": "ช็อต"},
                    {"name": "ไซรัปมิ้นท์สีฟ้าหรือเขียว", "amount": "20-30", "unit": "ml"},
                    {"name": "นมสดเย็น", "amount": "120", "unit": "ml"},
                    {"name": "น้ำแข็ง", "amount": "เต็มแก้ว", "unit": "แก้ว"}
                ],
                "equipment": ["เครื่องชง Espresso", "แก้วตวง", "ช้อนคน", "แก้วเสิร์ฟ"],
                "steps": [
                    {"step": 1, "action": "เทไซรัปมิ้นท์ลงก้นแก้วเสิร์ฟ"},
                    {"step": 2, "action": "เทนมสดเย็นผสมลงไปเบาๆ ให้เป็นชั้นสีฟ้า/เขียว"},
                    {"step": 3, "action": "ตักน้ำแข็งใส่เต็มแก้ว แล้วราดเอสเพรสโซ่ช็อตด้านบนสุด เกิดเป็น 3 ชั้นสี"}
                ]
            }
        ],
        "quiz": [
            {
                "question": "ข้อใดคือปัจจัยสำคัญที่สุดในการสกัดกาแฟให้ได้รสชาติกลมกล่อม (Perfect Extraction)",
                "answers": ["การบดเมล็ดกาแฟที่ถูกต้อง อุณหภูมิน้ำ 88-95°C แรงดัน 9 บาร์ และเวลา 25-30 วินาที"],
                "page": 51
            },
            {
                "question": "หากกาแฟสกัดออกมามีรสเปรี้ยวโดดและครีมม่าบาง เกิดจากสาเหตุใดและแก้ไขอย่างไร",
                "answers": ["เกิดจาก Under Extraction แก่โดยปรับเบอร์บดให้ละเอียดขึ้น หรือเพิ่มปริมาณผงกาแฟ"],
                "page": 52
            }
        ]
    }

# ============================================================
# 7. CLEAN & HIGH-PERFORMANCE NEO4J INGESTION
# ============================================================

def import_to_neo4j(pages: list, sbert_keywords_by_page: dict):
    print(f"🔌 Connecting to Neo4j at {NEO4J_URI}...")
    driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))
    
    with driver.session() as session:
        # Wipe old noisy relationship graph to ensure clean, accurate state
        print("🧹 Cleaning obsolete graph state...")
        session.run("MATCH (n) DETACH DELETE n")

        # Constraints
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (p:Page) REQUIRE p.number IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (k:Keyword) REQUIRE k.name IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (b:Beverage) REQUIRE b.name IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (s:Species) REQUIRE s.name IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (r:RoastLevel) REQUIRE r.name IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (g:GrindSize) REQUIRE g.name IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (ex:ExtractionStatus) REQUIRE ex.status IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (m:Module) REQUIRE m.id IS UNIQUE")
        session.run("CREATE CONSTRAINT IF NOT EXISTS FOR (d:Document) REQUIRE d.title IS UNIQUE")

        kb = get_curated_knowledge()

        # 1. Document & Modules
        print("Ingesting Document & Modules...")
        session.run("""
            MERGE (d:Document {title: 'คู่มือประกอบการฝึกอบรม หลักสูตร: บาริสต้ามืออาชีพ'})
            SET d.total_pages = 53, d.code = '241-351'
        """)
        for m in kb["modules"]:
            session.run("""
                MERGE (mod:Module {id: $id})
                SET mod.name = $name, mod.page_start = $ps, mod.page_end = $pe
                WITH mod
                MATCH (d:Document)
                MERGE (d)-[:HAS_MODULE]->(mod)
            """, id=m["id"], name=m["name"], ps=m["page_start"], pe=m["page_end"])

        # 2. Pages & SBERT Salient Keywords (Top 5-6 distinct per page)
        print("Ingesting Pages and Top Salient Keywords...")
        for p in pages:
            p_num = p["page"]
            clean_sample = " ".join(p["raw_text"].split())[:120]
            session.run("""
                MERGE (page:Page {number: $num})
                SET page.length = $length,
                    page.content_sample = $sample
                WITH page
                MATCH (d:Document)
                MERGE (d)-[:CONTAINS_PAGE]->(page)
            """, num=p_num, length=len(p["raw_text"]), sample=clean_sample)

            # Link Module to Page
            for m in kb["modules"]:
                if m["page_start"] <= p_num <= m["page_end"]:
                    session.run("""
                        MATCH (mod:Module {id: $id}), (page:Page {number: $num})
                        MERGE (mod)-[:COVERS_PAGE]->(page)
                    """, id=m["id"], num=p_num)

            # Link Salient SBERT Keywords (Top 5 only)
            kws = sbert_keywords_by_page.get(p_num, [])
            if kws:
                session.run("""
                    MATCH (page:Page {number: $num})
                    UNWIND $kws AS kw
                    MERGE (k:Keyword {name: kw.keyword})
                    SET k.type = kw.type, k.score = kw.score
                    MERGE (page)-[:HAS_KEYWORD]->(k)
                """, num=p_num, kws=kws)

        # 3. Species & Varieties
        print("Ingesting Species & Varieties...")
        for s in kb["species"]:
            session.run("""
                MERGE (sp:Species {name: $name})
                SET sp.world_share = $share
                WITH sp
                MERGE (e:Entity {name: $name})
                SET e.type = 'Species'
                MERGE (sp)-[:AS_ENTITY]->(e)
            """, name=s["name"], share=s["world_share"])
            for v in s["varieties"]:
                session.run("""
                    MATCH (sp:Species {name: $name})
                    MERGE (var:Variety {name: $v})
                    MERGE (sp)-[:HAS_VARIETY]->(var)
                    WITH var
                    MERGE (e:Entity {name: $v})
                    SET e.type = 'Variety'
                    MERGE (var)-[:AS_ENTITY]->(e)
                """, name=s["name"], v=v)

        # 4. 10 Steps from Tree to Cup (Pipeline Flow)
        print("Ingesting 10 Steps from Tree to Cup...")
        steps_data = kb["production_steps"]
        for s in steps_data:
            session.run("""
                MERGE (ps:ProductionStep {step_number: $num})
                SET ps.name = $name
                WITH ps
                MERGE (e:Entity {name: $name})
                SET e.type = 'ProductionStep'
                MERGE (ps)-[:AS_ENTITY]->(e)
            """, num=s["step"], name=s["name"])
        for idx in range(len(steps_data) - 1):
            session.run("""
                MATCH (s1:ProductionStep {step_number: $s1})
                MATCH (s2:ProductionStep {step_number: $s2})
                MERGE (s1)-[:PRECEDES]->(s2)
            """, s1=steps_data[idx]["step"], s2=steps_data[idx + 1]["step"])

        # 5. Roast Levels & Grind Sizes
        print("Ingesting Roast Levels and Grind Sizes...")
        for r in kb["roast_levels"]:
            session.run("""
                MERGE (roast:RoastLevel {name: $name})
                SET roast.agtron = $agtron
                WITH roast
                MERGE (e:Entity {name: $name})
                SET e.type = 'RoastLevel'
                MERGE (roast)-[:AS_ENTITY]->(e)
            """, name=r["name"], agtron=r["agtron"])

        for g in kb["grind_sizes"]:
            session.run("""
                MERGE (grind:GrindSize {name: $name})
                SET grind.equipment = $eq
                WITH grind
                MERGE (e:Entity {name: $name})
                SET e.type = 'GrindSize'
                MERGE (grind)-[:AS_ENTITY]->(e)
            """, name=g["name"], eq=g["eq"])

        # 6. Extraction Science & Diagnostic Tree
        print("Ingesting Extraction Science & Diagnostics...")
        for ex in kb["extraction_statuses"]:
            session.run("""
                MERGE (status:ExtractionStatus {status: $name})
                SET status.crema = $crema,
                    status.taste = $taste,
                    status.causes = $causes,
                    status.solutions = $solutions
                WITH status
                MERGE (e:Entity {name: $name})
                SET e.type = 'ExtractionStatus'
                MERGE (status)-[:AS_ENTITY]->(e)
            """, name=ex["status"], crema=ex["crema"], taste=ex["taste"], causes=ex["causes"], solutions=ex["solutions"])

        # Diagnostic branches
        diagnostic_cases = [
            {
                "status": "Under Extraction (สกัดน้อยเกินไป)",
                "causes": ["บดกาแฟหยาบเกินไป", "แทมป์เบาเกินไป", "ปริมาณผงกาแฟน้อยเกินไป", "อุณหภูมิน้ำต่ำกว่า 88°C"],
                "solutions": ["ปรับเบอร์บดให้ละเอียดขึ้น (Finer)", "เพิ่มปริมาณผงกาแฟเป็น 18-20 กรัม", "แทมป์ให้แน่นสม่ำเสมอ"]
            },
            {
                "status": "Over Extraction (สกัดมากเกินไป)",
                "causes": ["บดกาแฟละเอียดเกินไป", "แทมป์แน่นเกินไป", "ปริมาณผงกาแฟมากเกินไป", "อุณหภูมิน้ำสูงเกิน 95°C"],
                "solutions": ["ปรับเบอร์บดให้หยาบขึ้นเล็กน้อย (Coarser)", "แทมป์ด้วยแรงพอดี", "ลดอุณหภูมิน้ำลงให้อยู่ในช่วง 88-95°C"]
            }
        ]
        for case in diagnostic_cases:
            session.run("""
                MATCH (ex:ExtractionStatus {status: $status})
                FOREACH (c_name IN $causes |
                    MERGE (c:ExtractionCause {name: c_name})
                    MERGE (ex)-[:CAUSED_BY]->(c)
                )
                FOREACH (s_name IN $solutions |
                    MERGE (sol:ExtractionSolution {action: s_name})
                    MERGE (ex)-[:RESOLVED_BY]->(sol)
                )
            """, status=case["status"], causes=case["causes"], solutions=case["solutions"])

        # 7. Latte Art
        print("Ingesting Latte Art Science & Techniques...")
        la = kb["latte_art"]
        session.run("""
            MERGE (latte:LatteArt {name: $name})
            SET latte.steaming_temp = $temp
            WITH latte
            MERGE (e:Entity {name: $name})
            SET e.type = 'LatteArt'
            MERGE (latte)-[:AS_ENTITY]->(e)
        """, name=la["name"], temp=la["temp"])
        for tech in la["techniques"]:
            session.run("""
                MATCH (latte:LatteArt {name: $la_name})
                MERGE (t:LatteArtTechnique {name: $t_name})
                SET t.patterns = $patterns
                MERGE (latte)-[:HAS_TECHNIQUE]->(t)
                WITH t
                MERGE (e:Entity {name: $t_name})
                SET e.type = 'LatteArtTechnique'
                MERGE (t)-[:AS_ENTITY]->(e)
            """, la_name=la["name"], t_name=tech["name"], patterns=tech["patterns"])

        # 8. Beverages, Recipes, SOP Steps, Ingredients, Equipment
        print("Ingesting 13 Beverage Recipes, SOP Steps & Cross-Entity Edges...")
        for bev in kb["beverages"]:
            bev_name = bev["name"]
            page_num = bev["page"]

            # Beverage Node
            session.run("""
                MERGE (b:Beverage {name: $name})
                SET b.category = $cat,
                    b.roast_recommendation = $roast,
                    b.grind_recommendation = $grind,
                    b.page = $page
                WITH b
                MERGE (e:Entity {name: $name})
                SET e.type = 'Beverage'
                MERGE (b)-[:AS_ENTITY]->(e)
                WITH b
                MATCH (p:Page {number: $page})
                MERGE (p)-[:DESCRIBES_RECIPE]->(b)
                WITH b
                MATCH (m:Module {id: 'MOD_04'})
                MERGE (m)-[:HAS_RECIPE]->(b)
            """, name=bev_name, cat=bev["category"], roast=bev["roast"], grind=bev["grind"], page=page_num)

            # Ingredients
            for ing in bev.get("ingredients", []):
                session.run("""
                    MATCH (b:Beverage {name: $bev_name})
                    MERGE (i:Ingredient {name: $ing_name})
                    MERGE (b)-[r:USES_INGREDIENT]->(i)
                    SET r.amount = $amount, r.unit = $unit
                    WITH i
                    MERGE (e:Entity {name: $ing_name})
                    SET e.type = 'Ingredient'
                    MERGE (i)-[:AS_ENTITY]->(e)
                """, bev_name=bev_name, ing_name=ing["name"], amount=ing["amount"], unit=ing["unit"])

            # Equipment
            for eq in bev.get("equipment", []):
                session.run("""
                    MATCH (b:Beverage {name: $bev_name})
                    MERGE (equipment:Equipment {name: $eq_name})
                    MERGE (b)-[:USES_EQUIPMENT]->(equipment)
                    WITH equipment
                    MERGE (e:Entity {name: $eq_name})
                    SET e.type = 'Equipment'
                    MERGE (equipment)-[:AS_ENTITY]->(e)
                """, bev_name=bev_name, eq_name=eq)


            # Steps
            for st in bev.get("steps", []):
                step_id = f"{bev_name}_S{st['step']}"
                session.run("""
                    MATCH (b:Beverage {name: $bev_name})
                    MERGE (step:RecipeStep {id: $step_id})
                    SET step.step_number = $num, step.action = $action, step.beverage = $bev_name
                    MERGE (b)-[:HAS_STEP]->(step)
                """, bev_name=bev_name, step_id=step_id, num=st["step"], action=st["action"])

            # Sequential NEXT_STEP
            steps_list = sorted(bev.get("steps", []), key=lambda x: x["step"])
            for idx in range(len(steps_list) - 1):
                session.run("""
                    MATCH (s1:RecipeStep {id: $id1})
                    MATCH (s2:RecipeStep {id: $id2})
                    MERGE (s1)-[:NEXT_STEP]->(s2)
                """, id1=f"{bev_name}_S{steps_list[idx]['step']}",
                     id2=f"{bev_name}_S{steps_list[idx + 1]['step']}")

            # Link RoastLevel & GrindSize
            if "คั่วอ่อน" in bev["roast"]:
                session.run("MATCH (b:Beverage {name: $name}), (r:RoastLevel) WHERE r.name CONTAINS 'คั่วอ่อน' MERGE (b)-[:REQUIRES_ROAST]->(r)", name=bev_name)
            if "คั่วกลาง" in bev["roast"]:
                session.run("MATCH (b:Beverage {name: $name}), (r:RoastLevel) WHERE r.name CONTAINS 'คั่วกลาง' MERGE (b)-[:REQUIRES_ROAST]->(r)", name=bev_name)
            if "คั่วเข้ม" in bev["roast"]:
                session.run("MATCH (b:Beverage {name: $name}), (r:RoastLevel) WHERE r.name CONTAINS 'คั่วเข้ม' MERGE (b)-[:REQUIRES_ROAST]->(r)", name=bev_name)

            if "ละเอียดมาก" in bev["grind"]:
                session.run("MATCH (b:Beverage {name: $name}), (g:GrindSize) WHERE g.name CONTAINS 'ละเอียดมาก' MERGE (b)-[:RECOMMENDS_GRIND]->(g)", name=bev_name)
            elif "ค่อนข้างละเอียด" in bev["grind"] or "15 คลิก" in bev["grind"]:
                session.run("MATCH (b:Beverage {name: $name}), (g:GrindSize) WHERE g.name CONTAINS 'ค่อนข้างละเอียด' MERGE (b)-[:RECOMMENDS_GRIND]->(g)", name=bev_name)
            elif "ละเอียด" in bev["grind"]:
                session.run("MATCH (b:Beverage {name: $name}), (g:GrindSize) WHERE g.name CONTAINS 'ละเอียด (' OR g.name = 'ละเอียด (Fine)' MERGE (b)-[:RECOMMENDS_GRIND]->(g)", name=bev_name)
            elif "ปานกลาง" in bev["grind"]:
                session.run("MATCH (b:Beverage {name: $name}), (g:GrindSize) WHERE g.name CONTAINS 'ปานกลาง' MERGE (b)-[:RECOMMENDS_GRIND]->(g)", name=bev_name)

            # Target Perfect Extraction
            session.run("""
                MATCH (b:Beverage {name: $name}), (ex:ExtractionStatus {status: 'Espresso Perfect (Good Extraction)'})
                MERGE (b)-[:STRIVES_FOR]->(ex)
            """, name=bev_name)

            if "ลาเต้" in bev_name or "คาปูชิโน่" in bev_name:
                session.run("""
                    MATCH (b:Beverage {name: $name}), (la:LatteArt {name: 'ศาสตร์แห่งลาเต้อาร์ต'})
                    MERGE (b)-[:APPLIES_TECHNIQUE]->(la)
                """, name=bev_name)

        # 9. Quizzes
        print("Ingesting Barista Quizzes...")
        for q in kb["quiz"]:
            session.run("""
                MERGE (qq:QuizQuestion {question: $q_text})
                SET qq.answers = $ans, qq.page = $page
                WITH qq
                MATCH (m:Module {id: 'MOD_05'})
                MERGE (m)-[:HAS_QUIZ]->(qq)
            """, q_text=q["question"], ans=q["answers"], page=q["page"])

    driver.close()
    print("✅ Neo4j Knowledge Graph Ingestion Completed Successfully!")

# ============================================================
# 8. PIPELINE RUNNER
# ============================================================

def run_pipeline(use_llm: bool = False):
    print("=" * 65)
    print("☕ COFFEE BARISTA KNOWLEDGE GRAPH PIPELINE")
    if use_llm:
        print(f"Pipeline: PDF → SBERT Matrix + Ollama LLM ({OLLAMA_MODEL}) → Neo4j")
    else:
        print("Pipeline: PDF → SBERT Matrix (Fast Salient Filter) → Neo4j")
    print("=" * 65)

    pages = extract_pages_from_pdf(PDF_PATH)
    print(f"📖 Extracted {len(pages)} pages from '{PDF_PATH}'.")

    # Optional: Initialize Ollama LLM if requested via --llm
    llm_instance = None
    if use_llm:
        try:
            from langchain_ollama import ChatOllama
            print(f"🤖 Connecting to Ollama LLM ({OLLAMA_MODEL})...")
            llm_instance = ChatOllama(model=OLLAMA_MODEL, temperature=0.1)
            print("✅ Ollama LLM initialized successfully.")
        except Exception as e:
            print(f"⚠️ Ollama LLM Init Notice: {e}. Running with SBERT matrix only.")

    # SBERT Matrix Keyword Matcher (Top 5 Salient per page)
    matcher = SbertKeywordMatcher(EMBED_MODEL, COFFEE_ONTOLOGY)
    sbert_keywords_by_page = {}
    json_knowledge = []

    print("⚡ Extracting salient top keywords per page via SBERT matrix...")
    for p in pages:
        p_num = p["page"]
        text = p["raw_text"]
        if len(text.strip()) < 30:
            sbert_keywords_by_page[p_num] = []
            json_knowledge.append({"page": p_num, "summary": "หน้าว่างหรือปก", "keywords": []})
            continue

        # Extract top 5 salient keywords with threshold 0.58
        top_kws = matcher.extract_keywords(text, threshold=0.58, top_k=5)
        sbert_keywords_by_page[p_num] = top_kws

        page_summary = f"เนื้อหาหน้า {p_num}: " + ", ".join([k["keyword"] for k in top_kws[:3]])
        if llm_instance:
            try:
                prompt = (
                    f"คุณคือผู้เชี่ยวชาญบาริสต้า กรุณาสรุปเนื้อหาสำคัญของหน้า {p_num} ต่อไปนี้ให้กระชับ 1-2 ประโยคเป็นภาษาไทย:\n\n"
                    f"{text[:1000]}"
                )
                response = llm_instance.invoke(prompt)
                page_summary = response.content.strip()
                print(f"  [LLM] Page {p_num}: {page_summary[:60]}...")
            except Exception as e:
                print(f"  [LLM Warning] Page {p_num}: {e}")

        json_knowledge.append({
            "page": p_num,
            "summary": page_summary,
            "keywords": top_kws
        })

    # Save to JSON
    with open(JSON_OUTPUT_PATH, "w", encoding="utf-8") as f:
        json.dump({"pages": json_knowledge}, f, ensure_ascii=False, indent=2)
    print(f"💾 Knowledge saved to '{JSON_OUTPUT_PATH}'.")

    # Ingest clean, structured Knowledge Graph to Neo4j
    import_to_neo4j(pages, sbert_keywords_by_page)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Coffee Barista Knowledge Graph Pipeline")
    parser.add_argument("--llm", action="store_true", help="Enable Ollama LLM structured extraction for all pages")
    args = parser.parse_args()

    run_pipeline(use_llm=args.llm)
