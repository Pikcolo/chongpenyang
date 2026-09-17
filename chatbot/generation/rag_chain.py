"""
End-to-End RAG Chain orchestrating Dynamic Hybrid Retrieval, Guardrails,
Ollama LLM (qwen2.5:7b), Citation Engine, and Conversational History.
"""

from typing import Dict, Any, List
import json
from langchain_ollama import ChatOllama

from chatbot.config import settings
from chatbot.retrieval.dynamic_retriever import DynamicHybridRetriever
from chatbot.generation.prompt_templates import format_rag_prompt, build_chat_messages
from chatbot.generation.guardrails import GuardrailManager
from chatbot.generation.citation_engine import CitationEngine
from chatbot.ingestion.text_cleaner import clean_thai_text

class BaristaRAGChain:
    """Full Production-Grade Conversational RAG Pipeline."""

    def __init__(
        self,
        retriever: DynamicHybridRetriever,
        guardrails: GuardrailManager = None,
        llm: ChatOllama = None
    ):
        self.retriever = retriever
        self.guardrails = guardrails or GuardrailManager()
        self.citation_engine = CitationEngine()

        if llm is not None:
            self.llm = llm
        else:
            try:
                self.llm = ChatOllama(
                    model=settings.OLLAMA_MODEL,
                    base_url=settings.OLLAMA_BASE_URL,
                    temperature=settings.LLM_TEMPERATURE
                )
            except Exception as e:
                print(f"⚠️ Warning initializing Ollama LLM: {e}")
                self.llm = None

        # User session memory: { user_id: [ {"role": "user/assistant", "text": "..."}, ... ] }
        self.conversation_memory: Dict[str, List[Dict[str, str]]] = {}
        self.max_history_turns = 6

    def get_user_history_str(self, session_id: str) -> str:
        """Formats conversation history for prompt injection."""
        history = self.conversation_memory.get(session_id, [])
        if not history:
            return ""
        lines = []
        for msg in history:
            role = "ผู้ใช้" if msg["role"] == "user" else "บาริสต้า AI"
            lines.append(f"{role}: {msg['text']}")
        return "\n".join(lines)

    def add_user_history(self, session_id: str, role: str, text: str):
        """Appends message to session memory."""
        if session_id not in self.conversation_memory:
            self.conversation_memory[session_id] = []
        self.conversation_memory[session_id].append({"role": role, "text": text})
        if len(self.conversation_memory[session_id]) > self.max_history_turns:
            self.conversation_memory[session_id] = self.conversation_memory[session_id][-self.max_history_turns:]

    def answer_question(
        self,
        question: str,
        session_id: str = "default_user",
        append_citations: bool = True
    ) -> Dict[str, Any]:
        """
        Executes end-to-end question answering pipeline:
        1. Dynamic Hybrid Retrieval
        2. Pre-generation Guardrail check
        3. Prompt engineering with CoT
        4. Ollama Generation
        5. Post-generation validation & Citation formatting
        """
        # 0. Check for friendly greeting / identity introduction
        clean_q = question.strip().lower()
        greeting_words = ["สวัสดี", "หวัดดี", "ดีครับ", "ดีค่ะ", "hello", "hi", "hey", "คุณคือใคร", "แนะนำตัว", "ทำอะไรได้บ้าง", "ช่วยอะไรได้บ้าง"]
        coffee_keywords = ["สูตร", "องศา", "บาร์", "บด", "สกัด", "เอสเพรสโซ่", "ลาเต้", "อเมริกาโน่", "คั่ว", "agtron", "ช็อต", "นม", "อาราบิก้า", "โรบัสต้า", "ปัญหา", "เปรี้ยว", "ขม"]
        is_greeting = any(w in clean_q for w in greeting_words) and len(clean_q) <= 40
        has_coffee_intent = any(k in clean_q for k in coffee_keywords)

        if is_greeting and not has_coffee_intent:
            greeting_reply = (
                "สวัสดีครับ! ผมคือ \"SmartDoc Barista AI\" ผู้ช่วยผู้เชี่ยวชาญด้านศาสตร์แห่งกาแฟและบาริสต้ามืออาชีพ ☕\n\n"
                "ผมพร้อมให้คำแนะนำข้อมูลตามคู่มือหลักสูตรบาริสต้ามืออาชีพ เช่น:\n"
                "• 📖 สูตรและวิธีทำเครื่องดื่มตาม SOP (Espresso, Americano, กาแฟส้ม, กาแฟพีช, ลาเต้มิ้นท์, กาแฟน้ำผึ้งมะนาว ฯลฯ)\n"
                "• ⚙️ เทคนิคการสกัด Perfect Shot (อุณหภูมิ 90-96°C, แรงดัน 9-10 บาร์, เวลา 20-30 วินาที)\n"
                "• 🔬 วิเคราะห์และแก้ปัญหารสชาติ Under-Extraction / Over-Extraction\n"
                "• 🥛 วิทยาศาสตร์การสตีมนมและประวัติศาสตร์ Latte Art\n\n"
                "วันนี้สนใจสอบถามสูตรหรือข้อมูลเทคนิคด้านใด พิมพ์ถามได้เลยครับ!"
            )
            self.add_user_history(session_id, "user", question)
            self.add_user_history(session_id, "assistant", greeting_reply)
            return {
                "question": question,
                "answer": greeting_reply,
                "raw_answer": greeting_reply,
                "citations": [],
                "contexts": [],
                "dynamic_k": 0,
                "guardrail_triggered": False
            }

        # 1. Retrieve contexts
        retrieval_output = self.retriever.retrieve(question)
        contexts = retrieval_output["contexts"]
        dynamic_k = retrieval_output["dynamic_k"]

        # 2. Pre-generation Guardrail
        is_valid, fallback_msg = self.guardrails.validate_retrieval(contexts, query=question)
        if not is_valid:
            self.add_user_history(session_id, "user", question)
            self.add_user_history(session_id, "assistant", fallback_msg)
            return {
                "question": question,
                "answer": fallback_msg,
                "raw_answer": fallback_msg,
                "citations": [],
                "contexts": [],
                "dynamic_k": dynamic_k,
                "guardrail_triggered": True
            }

        # 3. Format Context and Prompt
        context_blocks = []
        for idx, c in enumerate(contexts, start=1):
            source_tag = f"[เอกสารอ้างอิงลำดับที่ {idx} | หน้า {c['page']} ({c['topic_title']})]"
            cleaned_content = clean_thai_text(c['content'])
            context_blocks.append(f"{source_tag}\n{cleaned_content}")
        full_context_str = "\n\n".join(context_blocks)

        history_str = self.get_user_history_str(session_id)
        chat_messages = build_chat_messages(
            query=question,
            context_text=full_context_str,
            chat_history=history_str
        )

        # 4. Generate with LLM
        if not self.llm:
            raw_answer = "❌ ไม่สามารถเชื่อมต่อกับ Ollama LLM ได้ กรุณาตรวจสอบว่า Ollama กำลังรันอยู่"
        else:
            try:
                response = self.llm.invoke(chat_messages)
                raw_answer = response.content if hasattr(response, "content") else str(response)
            except Exception as e:
                # Fallback to single string prompt if chat messages format encounters error
                try:
                    prompt = format_rag_prompt(question, full_context_str, history_str)
                    response = self.llm.invoke(prompt)
                    raw_answer = response.content if hasattr(response, "content") else str(response)
                except Exception as inner_e:
                    raw_answer = f"⚠️ เกิดข้อผิดพลาดในการเรียก LLM: {inner_e}"

        # 5. Post-generation Guardrail
        cleaned_answer = self.guardrails.validate_generation(question, raw_answer, contexts)

        # 6. Extract & Attach Citations
        citations = self.citation_engine.extract_citations(contexts)
        final_answer = cleaned_answer
        if append_citations and citations and "ไม่มีระบุในคู่มือ" not in cleaned_answer:
            citation_footer = self.citation_engine.format_markdown_footer(citations)
            final_answer += citation_footer

        # Save to memory
        self.add_user_history(session_id, "user", question)
        self.add_user_history(session_id, "assistant", cleaned_answer)

        return {
            "question": question,
            "answer": final_answer,
            "raw_answer": cleaned_answer,
            "citations": citations,
            "contexts": contexts,
            "dynamic_k": dynamic_k,
            "guardrail_triggered": False
        }
