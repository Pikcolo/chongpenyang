"""
Configuration loader supporting .env and config.yaml.
Provides unified dataclass / singleton config for the chatbot project.
"""

import os
from pathlib import Path
import yaml
from dotenv import load_dotenv

# Load root .env
ROOT_DIR = Path(__file__).resolve().parent.parent
load_dotenv(ROOT_DIR / ".env")

# Locate config.yaml (prioritize root, then chatbot/)
CONFIG_YAML_PATH = ROOT_DIR / "config.yaml"
if not CONFIG_YAML_PATH.exists():
    CONFIG_YAML_PATH = ROOT_DIR / "chatbot" / "config.yaml"

yaml_data = {}
if CONFIG_YAML_PATH.exists():
    try:
        with open(CONFIG_YAML_PATH, "r", encoding="utf-8") as f:
            yaml_data = yaml.safe_load(f) or {}
    except Exception as e:
        print(f"⚠️ Warning loading config.yaml: {e}")

class Settings:
    # Document
    PDF_PATH = os.getenv(
        "PDF_PATH",
        yaml_data.get("document", {}).get("pdf_path", str(ROOT_DIR / "documents.pdf"))
    )
    if not os.path.isabs(PDF_PATH):
        PDF_PATH = str(ROOT_DIR / PDF_PATH)

    # Embedding (Default to SOTA BAAI/bge-m3)
    EMBED_MODEL = os.getenv(
        "EMBED_MODEL",
        yaml_data.get("embedding", {}).get("model_name", "BAAI/bge-m3")
    )
    EMBED_DEVICE = os.getenv("EMBED_DEVICE", yaml_data.get("embedding", {}).get("device", "cpu"))

    # Vector Stores (FAISS as primary)
    VECTOR_STORE_TYPE = os.getenv(
        "VECTOR_STORE_TYPE",
        yaml_data.get("vector_store", {}).get("type", "faiss")
    ).lower()
    
    CHROMA_PATH = os.getenv(
        "CHROMA_PATH",
        yaml_data.get("vector_store", {}).get("chroma_path", str(ROOT_DIR / "chatbot" / "data" / "chroma_db"))
    )
    if not os.path.isabs(CHROMA_PATH):
        CHROMA_PATH = str(ROOT_DIR / CHROMA_PATH)

    FAISS_PATH = os.getenv(
        "FAISS_PATH",
        yaml_data.get("vector_store", {}).get("faiss_path", str(ROOT_DIR / "chatbot" / "data" / "faiss_index"))
    )
    if not os.path.isabs(FAISS_PATH):
        FAISS_PATH = str(ROOT_DIR / FAISS_PATH)

    COLLECTION_NAME = os.getenv(
        "COLLECTION_NAME",
        yaml_data.get("vector_store", {}).get("collection_name", "barista_rag_collection")
    )

    # Fusion
    FUSION_ALGORITHM = os.getenv("FUSION_ALGORITHM", yaml_data.get("fusion", {}).get("algorithm", "rrf")).lower()
    RRF_K = int(os.getenv("RRF_K", yaml_data.get("fusion", {}).get("rrf_k", 60)))
    DENSE_WEIGHT = float(os.getenv("DENSE_WEIGHT", yaml_data.get("fusion", {}).get("dense_weight", 0.5)))
    SPARSE_WEIGHT = float(os.getenv("SPARSE_WEIGHT", yaml_data.get("fusion", {}).get("sparse_weight", 0.5)))

    # Re-ranker (can be disabled via RERANKER_ENABLED=false to use Pure RRF / Fusion without extra model)
    reranker_env = os.getenv("RERANKER_ENABLED")
    if reranker_env is not None:
        RERANKER_ENABLED = reranker_env.strip().lower() in ("true", "1", "yes")
    else:
        RERANKER_ENABLED = yaml_data.get("reranker", {}).get("enabled", False)

    RERANKER_MODEL = os.getenv(
        "RERANKER_MODEL",
        yaml_data.get("reranker", {}).get("model_name", "")
    )
    RERANKER_TOP_N = int(os.getenv("RERANKER_TOP_N", yaml_data.get("reranker", {}).get("top_n", 4)))

    # Dynamic Optimization
    TOP_K_DEFAULT = int(os.getenv("TOP_K", yaml_data.get("dynamic_optimization", {}).get("default_top_k", 5)))
    MIN_TOP_K = int(os.getenv("MIN_TOP_K", yaml_data.get("dynamic_optimization", {}).get("min_top_k", 3)))
    MAX_TOP_K = int(os.getenv("MAX_TOP_K", yaml_data.get("dynamic_optimization", {}).get("max_top_k", 8)))
    MAX_CONTEXT_TOKENS = int(os.getenv("MAX_CONTEXT_TOKENS", yaml_data.get("dynamic_optimization", {}).get("max_context_tokens", 2200)))

    # LLM
    OLLAMA_MODEL = os.getenv(
        "OLLAMA_MODEL",
        yaml_data.get("llm", {}).get("model", "qwen2.5:3b")
    )
    OLLAMA_BASE_URL = os.getenv(
        "OLLAMA_BASE_URL",
        yaml_data.get("llm", {}).get("base_url", "http://localhost:11434")
    )
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", yaml_data.get("llm", {}).get("temperature", 0.1)))

    # Guardrails
    STRICT_CONTEXT_CHECK = os.getenv("STRICT_CONTEXT_CHECK", "true").lower() in ("true", "1", "yes")
    MIN_SIMILARITY_THRESHOLD = float(os.getenv("MIN_SIMILARITY_THRESHOLD", yaml_data.get("guardrails", {}).get("min_similarity_threshold", 0.05)))
    FALLBACK_MESSAGE = os.getenv(
        "FALLBACK_MESSAGE",
        yaml_data.get(
            "guardrails", {}
        ).get("fallback_message", "ขออภัยครับ ข้อมูลดังกล่าวไม่มีระบุในคู่มือบาริสต้ามืออาชีพที่กำหนด ทางเราจึงไม่สามารถให้คำตอบนอกเหนือจากเอกสารได้ครับ")
    )

    # LINE & Server
    CHANNEL_ACCESS_TOKEN = os.getenv("CHANNEL_ACCESS_TOKEN", "")
    CHANNEL_SECRET = os.getenv("CHANNEL_SECRET", "")
    PORT = int(os.getenv("WEBHOOK_PORT", yaml_data.get("server", {}).get("port", 5000)))
    HOST = os.getenv("SERVER_HOST", yaml_data.get("server", {}).get("host", "0.0.0.0"))

settings = Settings()
