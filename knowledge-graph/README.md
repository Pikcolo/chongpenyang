# Coffee Barista Knowledge Graph (Neo4j)

ส่วนงานระบบ **Knowledge Graph บน Neo4j** สกัดข้อมูลจากคู่มือบาริสต้ามืออาชีพ 53 หน้า (`documents.pdf`)

## 🌟 โครงสร้างข้อมูลใน Graph
- **359 Nodes & 773 Relationships**: ครอบคลุมพฤกษศาสตร์กาแฟ, 10 ขั้นตอนจากต้นสู่แก้ว, ระดับการคั่ว (Agtron), วิทยาศาสตร์การสกัด (Under / Perfect / Over-extraction), อุปกรณ์, เทคนิคลาเต้อาร์ต และ 13 สูตรเครื่องดื่มมาตรฐาน
- **Domain Ontology**:
  - `Beverage`, `Ingredient`, `Equipment`, `RecipeStep`
  - `RoastLevel`, `CoffeeBean`, `ExtractionStatus`, `DefectCause`, `Solution`

## 📁 โครงสร้างโฟลเดอร์
```
knowledge-graph/
├── docker-compose.yml             # Neo4j 5 Community container orchestration
├── feed_graph.py                  # สคริปต์สกัด Ontology & Ingest เข้า Neo4j
├── check_graph.py                 # ตรวจสอบสถิติจำนวน Node & Relation ใน Graph
├── page_knowledge.json            # ไฟล์ความรู้เชิงโครงสร้างที่สกัดไว้
├── neo4j_db/                      # ฐานข้อมูล Neo4j ที่บันทึกไว้ใน Local Disk
├── docs/
│   ├── graph-schema.md            # โครงสร้าง Schema และตัวอย่าง Cypher Query
│   └── knowledge-graph-summary.md # รายงานสรุปความรู้และ Ontology ใน Graph
└── tests/
    └── test_kg.py                 # Automated Unit Tests สำหรับตรวจสอบ Graph
```

## 🚀 การใช้งาน (Quick Start)
1. สตาร์ท Neo4j ผ่าน Docker:
   ```bash
   cd knowledge-graph
   docker compose up -d
   ```
   (เปิด Neo4j Browser ที่ `http://localhost:7474` โดยใช้ user: `neo4j`, password: `password1234`)

2. Ingest ข้อมูลเข้า Neo4j (ถ้าต้องการรันใหม่):
   ```bash
   python feed_graph.py
   ```

3. ตรวจสอบข้อมูลใน Graph:
   ```bash
   python check_graph.py
   ```

4. รันแบบทดสอบอัตโนมัติ:
   ```bash
   pytest tests/test_kg.py
   ```
