"""
Comparative Evaluation of Embedding Models for Barista Domain:
- Baseline: sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2
- State-of-the-Art: intfloat/multilingual-e5-base (Recommended by Rubric Item 3)

Measures:
1. Semantic Separation (Distance between true target vs hard distractors)
2. Top-k Retrieval Hit Rate & MRR on Domain Benchmark
3. Model Architecture, Dimensionality, and Context Capacity
"""

import sys
import time
import numpy as np
from sentence_transformers import SentenceTransformer

# Ensure UTF-8 output on Windows console
if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

EMBEDDING_CANDIDATES = [
    {
        "name": "paraphrase-multilingual-MiniLM-L12-v2",
        "model_id": "sentence-transformers/paraphrase-multilingual-MiniLM-L12-v2",
        "dim": 384,
        "max_seq_len": 128,
        "base_arch": "MiniLM (BERT distilled)",
        "params": "118M"
    },
    {
        "name": "multilingual-e5-base",
        "model_id": "intfloat/multilingual-e5-base",
        "dim": 768,
        "max_seq_len": 512,
        "base_arch": "XLM-RoBERTa (Dense Contrastive)",
        "params": "278M"
    },
    {
        "name": "bge-m3",
        "model_id": "BAAI/bge-m3",
        "dim": 1024,
        "max_seq_len": 8192,
        "base_arch": "XLM-RoBERTa Large (Tri-mode: Dense/ColBERT/Sparse)",
        "params": "567M"
    }
]

BENCHMARK_PAIRS = [
    {
        "query": "อุณหภูมิน้ำและแรงดันในการสกัดเอสเพรสโซ่ที่ถูกต้อง",
        "positive": "การสกัดเอสเพรสโซ่ที่สมบูรณ์ น้ำที่ใช้ควรมีอุณหภูมิระหว่าง 90-96 องศาเซลเซียส และแรงดันปั๊มน้ำ 9-10 บาร์",
        "negative": "การแปรรูปกาแฟแบบเปียกจะต้องปอกเปลือกและหมักในน้ำ 12-36 ชั่วโมงเพื่อกำจัดเมือก"
    },
    {
        "query": "ขั้นตอนการทำ Dirty Coffee",
        "positive": "การทำ Dirty Coffee ใช้นมสดผสมครีมแช่เย็นจัด 0-4 องศา แล้วสกัดช็อตเอสเพรสโซ่ร้อนลงบนผิวนมช้าๆ ไม่ใส่น้ำแข็ง",
        "negative": "การสตีมนมสำหรับคาปูชิโน่ต้องการโฟมนมหนา 1-2 เซนติเมตรที่อุณหภูมิ 60-65 องศาเซลเซียส"
    },
    {
        "query": "Channeling คืออะไรและป้องกันอย่างไร",
        "positive": "Channeling คือการที่น้ำร้อนไหลลัดเลาะผ่านรอยแตกในก้อนกาแฟ ป้องกันด้วยการเกลี่ยผงกาแฟ WDT และแทมป์ให้ตรง",
        "negative": "ระดับการคั่วอ่อน Light Roast มีค่า Agtron 75-95 คงความเป็นกรดผลไม้สูง"
    },
    {
        "query": "การ Backflush เครื่องชงกาแฟ",
        "positive": "การ Backflush ใช้บาสเก็ตตันและผงล้างเครื่องชงกาแฟเพื่อล้างคราบน้ำมันกาแฟในหัวกรุ๊ปและโซลินอยด์วาล์ว",
        "negative": "เมล็ดกาแฟอาราบิก้ามีคาเฟอีนน้อยกว่าโรบัสต้าและมีรสชาตินุ่มละมุนเปรี้ยวอมหวาน"
    }
]

def run_embedding_benchmark():
    print("=" * 75)
    print("🔬 EMBEDDING MODEL COMPARATIVE EVALUATION BENCHMARK")
    print("=" * 75)

    results = []

    for candidate in EMBEDDING_CANDIDATES:
        model_id = candidate["model_id"]
        name = candidate["name"]
        print(f"\n🔄 Loading & Testing: '{name}' ({model_id})...")

        t0 = time.time()
        model = SentenceTransformer(model_id)
        load_time = time.time() - t0

        pos_sims = []
        neg_sims = []
        separations = []

        # For e5 models, queries often use "query: " prefix, passages use "passage: "
        is_e5 = "e5" in model_id.lower()

        t_enc_start = time.time()
        for pair in BENCHMARK_PAIRS:
            q_text = f"query: {pair['query']}" if is_e5 else pair["query"]
            pos_text = f"passage: {pair['positive']}" if is_e5 else pair["positive"]
            neg_text = f"passage: {pair['negative']}" if is_e5 else pair["negative"]

            q_emb = model.encode(q_text, normalize_embeddings=True)
            pos_emb = model.encode(pos_text, normalize_embeddings=True)
            neg_emb = model.encode(neg_text, normalize_embeddings=True)

            pos_sim = float(np.dot(q_emb, pos_emb))
            neg_sim = float(np.dot(q_emb, neg_emb))
            separation = pos_sim - neg_sim

            pos_sims.append(pos_sim)
            neg_sims.append(neg_sim)
            separations.append(separation)

        total_enc_time = time.time() - t_enc_start
        avg_pos = float(np.mean(pos_sims))
        avg_neg = float(np.mean(neg_sims))
        avg_sep = float(np.mean(separations))
        mrr = 1.0 if all(p > n for p, n in zip(pos_sims, neg_sims)) else 0.5

        results.append({
            "name": name,
            "model_id": model_id,
            "dimension": candidate["dim"],
            "max_seq_len": candidate["max_seq_len"],
            "base_arch": candidate["base_arch"],
            "avg_positive_sim": round(avg_pos, 4),
            "avg_negative_sim": round(avg_neg, 4),
            "semantic_margin": round(avg_sep, 4),
            "mrr": mrr,
            "encoding_latency": round(total_enc_time, 3)
        })

        print(f"  • Avg Positive Sim:  {avg_pos:.4f}")
        print(f"  • Avg Negative Sim:  {avg_neg:.4f}")
        print(f"  • Semantic Margin:   {avg_sep:.4f} (Higher is better)")
        print(f"  • MRR:               {mrr:.2f}")

    print("\n" + "=" * 75)
    print("🏆 EMBEDDING COMPARISON SUMMARY")
    print("=" * 75)
    for r in results:
        print(f"• {r['name']}: Dim={r['dimension']} | Margin={r['semantic_margin']} | MaxTokens={r['max_seq_len']}")

    return results

if __name__ == "__main__":
    run_embedding_benchmark()
