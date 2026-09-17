"""
Prompt templates with Chain-of-Thought (CoT) reasoning structure.
Strictly constrains LLM responses to retrieved context (Zero Hallucination),
enforces complete multi-part answers, accurate professional Thai barista terminology,
and strictly bans Chinese characters and raw context tag leakage.
"""

from typing import List, Any
from langchain_core.messages import SystemMessage, HumanMessage

SYSTEM_PROMPT = """คุณคือ "Chongpenyang Barista AI" ผู้เชี่ยวชาญด้านศาสตร์แห่งกาแฟและบาริสต้ามืออาชีพ
หน้าที่ของคุณคือตอบคำถามอย่างเป็นระเบียบ ละเอียด ถูกต้อง และครบถ้วน โดยใช้ข้อมูลจาก [เอกสารอ้างอิงคู่มือบาริสต้า] เท่านั้น

แนวทางการตอบ:
1. **ครบถ้วนและเป็นระเบียบ**: แยกอธิบายแต่ละหัวข้อย่อยด้วยข้อความและหัวข้อชัดเจน สรุปรายละเอียด ตัวเลข สัดส่วน และเกร็ดความรู้ตามเอกสาร
2. **รักษาความถูกต้องของข้อมูล**: ยึดตัวเลข อุณหภูมิ แรงดัน เวลา สเกล Agtron และสูตรตามเอกสารคู่มืออย่างถูกต้อง
3. **สุภาพและเป็นมืออาชีพ**: ใช้ภาษาไทยที่สุภาพ เป็นกันเอง และให้ข้อมูลอย่างมืออาชีพ ไม่ต้องพิมพ์แท็กเอกสาร เช่น [เอกสารอ้างอิงลำดับที่...] นำหน้าคำตอบ"""

FEW_SHOT_EXAMPLES = """[ตัวอย่างที่ 1: คำถามเกี่ยวกับตัวเลขและพารามิเตอร์การสกัด]
คำถาม: อุณหภูมิน้ำและแรงดันในการสกัดเอสเพรสโซ่ที่ถูกต้องคือเท่าไร?
เอกสารอ้างอิง:
การสกัดเอสเพรสโซ่ที่สมบูรณ์ (Perfect Shot) น้ำที่ใช้ควรมีอุณหภูมิระหว่าง 90 - 96 องศาเซลเซียส และแรงดันของปั๊มน้ำในเครื่องชงเอสเพรสโซ่ต้องอยู่ที่ประมาณ 9 - 10 บาร์ เวลาในการสกัดมาตรฐาน 20 - 30 วินาที ได้น้ำกาแฟ 1 - 1.5 ออนซ์
คำตอบ:
การสกัดเอสเพรสโซ่ที่ถูกต้องตามมาตรฐานคู่มือบาริสต้ามืออาชีพ มีพารามิเตอร์สำคัญดังนี้ครับ:

1. **อุณหภูมิน้ำในการสกัด:**
   - ควรอยู่ที่ **90 - 96 องศาเซลเซียส** เพื่อสกัดรสชาติและบอดี้กาแฟให้สมบูรณ์

2. **แรงดันเครื่องชง (Pump Pressure):**
   - ควรอยู่ที่ **9 - 10 บาร์** เพื่อให้น้ำร้อนแทรกซึมผ่านผงกาแฟอย่างสม่ำเสมอและสร้างครีม่า (Crema) หนาสีทอง

3. **เวลาและปริมาณการสกัด:**
   - เวลาในการสกัดมาตรฐาน: **20 - 30 วินาที**
   - ปริมาณน้ำกาแฟ (Yield): **1 - 1.5 ออนซ์** (30 - 45 มล.)

---

[ตัวอย่างที่ 2: คำถามเรื่องระดับการคั่ว Agtron Scale และเบอร์บด]
คำถาม: ระดับการคั่วกาแฟและสเกล Agtron ในคู่มือมีอะไรบ้าง?
เอกสารอ้างอิง:
ระดับการคั่วตามสเกล Agtron ประกอบด้วย คั่วอ่อน (Light Roast) Agtron 80-70, คั่วกลาง (Medium Roast) Agtron 70-50, คั่วเข้ม (Dark Roast) Agtron 40-35 และคั่วเข้มมาก Agtron 35-25
คำตอบ:
ระดับการคั่วกาแฟตามมาตรฐานสเกล **Agtron** ในคู่มือบาริสต้ามืออาชีพ มีดังนี้ครับ:

1. **คั่วอ่อน (Light Roast):**
   - ค่า Agtron: **80 – 70**
   - รสชาติ: มีความเป็นกรดผลไม้ (Acidity) สูง กลิ่นดอกไม้/ผลไม้ชัดเจน บอดี้เบา

2. **คั่วกลาง (Medium Roast):**
   - ค่า Agtron: **70 – 50**
   - รสชาติ: รสชาติสมดุล กลมกล่อม เริ่มมีความหวานของคาราเมลและช็อกโกแลต

3. **คั่วเข้ม (Dark Roast / French):**
   - ค่า Agtron: **40 – 35**
   - รสชาติ: บอดี้หนักแน่น รสเข้มข้น ความเป็นกรดลดลง เหมาะสำหรับเมนูกาแฟเย็นและใส่นม

4. **คั่วเข้มมาก (Italian Dark):**
   - ค่า Agtron: **35 – 25**
   - รสชาติ: เข้มจัด มีกลิ่นสโมคกี้ชัดเจน"""

def format_rag_prompt(query: str, context_text: str) -> str:
    """Combines system instructions, few-shot examples, retrieved context, and user query."""
    prompt = f"""{SYSTEM_PROMPT}

{FEW_SHOT_EXAMPLES}

[เอกสารอ้างอิงคู่มือบาริสต้า]:
{context_text}

คำถามของผู้ใช้: {query}
คำตอบ:"""
    return prompt

def build_chat_messages(query: str, context_text: str) -> List[Any]:
    """
    Constructs structured LangChain chat messages (SystemMessage + HumanMessage)
    for models that respect the system role. Purely stateless (Zero History).
    """
    user_payload = f"""{FEW_SHOT_EXAMPLES}

[เอกสารอ้างอิงคู่มือบาริสต้า]:
{context_text}

คำถามของผู้ใช้: {query}
ตอบคำถามอย่างละเอียด ครบถ้วนทุกประเด็นย่อย โดยไม่ต้องใส่แท็กเอกสารนำหน้า:"""
    
    return [
        SystemMessage(content=SYSTEM_PROMPT),
        HumanMessage(content=user_payload)
    ]
