import os
import sys
from dotenv import load_dotenv
from neo4j import GraphDatabase

if hasattr(sys.stdout, 'reconfigure'):
    sys.stdout.reconfigure(encoding='utf-8')

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

if not NEO4J_URI or not NEO4J_PASSWORD:
    raise ValueError("❌ กรุณากำหนด NEO4J_URI และ NEO4J_PASSWORD ในไฟล์ .env ให้ครบถ้วน")

driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

print("=" * 65)
print("📊 NEO4J KNOWLEDGE GRAPH VERIFICATION")
print("=" * 65)

with driver.session() as session:
    # 1. Total Nodes
    tot_nodes = session.run("MATCH (n) RETURN count(n) AS count").single()["count"]
    # 2. Total Relationships
    tot_rels = session.run("MATCH ()-[r]->() RETURN count(r) AS count").single()["count"]
    print(f"📌 Total Nodes: {tot_nodes}")
    print(f"🔗 Total Relationships: {tot_rels}")

    print("\n--- Nodes by Label ---")
    label_res = session.run("""
        CALL db.labels() YIELD label
        CALL apoc.cypher.run('MATCH (n:`' + label + '`) RETURN count(n) as c', {}) YIELD value
        RETURN label, value.c as count ORDER BY count DESC
    """)
    for r in label_res:
        print(f"  • {r['label']}: {r['count']}")

    print("\n--- Relationships by Type ---")
    rel_res = session.run("""
        CALL db.relationshipTypes() YIELD relationshipType
        CALL apoc.cypher.run('MATCH ()-[r:`' + relationshipType + '`]->() RETURN count(r) as c', {}) YIELD value
        RETURN relationshipType, value.c as count ORDER BY count DESC
    """)
    for r in rel_res:
        print(f"  • {r['relationshipType']}: {r['count']}")

    print("\n--- Sample Query: Recipe for คาปูชิโน่เย็น (Iced Cappuccino) ---")
    q_cappuccino = """
    MATCH (b:Beverage)
    WHERE b.name CONTAINS 'คาปูชิโน่เย็น'
    OPTIONAL MATCH (b)-[ri:USES_INGREDIENT]->(i:Ingredient)
    OPTIONAL MATCH (b)-[:USES_EQUIPMENT]->(eq:Equipment)
    OPTIONAL MATCH (b)-[:HAS_STEP]->(st:RecipeStep)
    RETURN b.name AS beverage,
           b.category AS category,
           b.roast_recommendation AS roast,
           b.grind_recommendation AS grind,
           collect(DISTINCT i.name + ' (' + ri.amount + ' ' + ri.unit + ')') AS ingredients,
           collect(DISTINCT eq.name) AS equipment,
           collect(DISTINCT toString(st.step_number) + '. ' + st.action) AS steps
    """
    res = session.run(q_cappuccino).single()
    if res:
        print(f"Beverage: {res['beverage']} ({res['category']})")
        print(f"Roast: {res['roast']}")
        print(f"Grind: {res['grind']}")
        print(f"Ingredients: {', '.join(res['ingredients'])}")
        print(f"Equipment: {', '.join(res['equipment'])}")
        print(f"Steps:")
        for s in sorted(res['steps']):
            print(f"   {s}")

    print("\n--- Sample Query: Under Extraction Diagnosis ---")
    q_ext = """
    MATCH (ex:ExtractionStatus)
    RETURN ex.status AS status, ex.crema AS crema, ex.taste AS taste, ex.causes AS causes, ex.solutions AS solutions
    """
    res_ext = session.run(q_ext)
    for r in res_ext:
        print(f"\n[Status]: {r['status']}")
        print(f"  Crema: {r['crema']}")
        print(f"  Taste: {r['taste']}")
        print(f"  Causes: {r['causes']}")
        print(f"  Solutions: {r['solutions']}")

driver.close()
print("\n✅ Verification finished!")
