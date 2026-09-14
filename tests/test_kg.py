import os
import sys
import unittest
from dotenv import load_dotenv
from neo4j import GraphDatabase

load_dotenv()

NEO4J_URI = os.getenv("NEO4J_URI")
NEO4J_USER = os.getenv("NEO4J_USERNAME") or os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD")

if not NEO4J_URI or not NEO4J_PASSWORD:
    raise ValueError("❌ กรุณากำหนด NEO4J_URI และ NEO4J_PASSWORD ในไฟล์ .env ให้ครบถ้วน")

class TestCoffeeKnowledgeGraph(unittest.TestCase):

    @classmethod
    def setUpClass(cls):
        cls.driver = GraphDatabase.driver(NEO4J_URI, auth=(NEO4J_USER, NEO4J_PASSWORD))

    @classmethod
    def tearDownClass(cls):
        cls.driver.close()

    def test_01_neo4j_connectivity(self):
        """Verify that Neo4j can be queried and returns results."""
        with self.driver.session() as session:
            result = session.run("RETURN 1 AS val").single()
            self.assertEqual(result["val"], 1)

    def test_02_node_count_threshold(self):
        """Verify that the Knowledge Graph contains at least 300 nodes."""
        with self.driver.session() as session:
            count = session.run("MATCH (n) RETURN count(n) AS count").single()["count"]
            self.assertGreaterEqual(count, 300, f"Expected >= 300 nodes, found {count}")

    def test_03_relationship_count_threshold(self):
        """Verify that the Knowledge Graph contains at least 400 relationships."""
        with self.driver.session() as session:
            count = session.run("MATCH ()-[r]->() RETURN count(r) AS count").single()["count"]
            self.assertGreaterEqual(count, 400, f"Expected >= 400 relationships, found {count}")

    def test_04_beverage_recipes_complete(self):
        """Verify that all standard beverage recipes are present with ingredients and steps."""
        with self.driver.session() as session:
            res = session.run("""
                MATCH (b:Beverage)
                OPTIONAL MATCH (b)-[:USES_INGREDIENT]->(i:Ingredient)
                OPTIONAL MATCH (b)-[:HAS_STEP]->(s:RecipeStep)
                RETURN b.name AS name, count(DISTINCT i) AS ing_count, count(DISTINCT s) AS step_count
            """).data()
            self.assertGreaterEqual(len(res), 10, "Should have at least 10 coffee recipes")
            for r in res:
                self.assertGreater(r["ing_count"], 0, f"Recipe '{r['name']}' has no ingredients linked")
                self.assertGreater(r["step_count"], 0, f"Recipe '{r['name']}' has no steps linked")

    def test_05_extraction_troubleshooting(self):
        """Verify that Under and Over extraction diagnosis statuses exist with solutions."""
        with self.driver.session() as session:
            res = session.run("""
                MATCH (ex:ExtractionStatus)
                RETURN ex.status AS status, ex.crema AS crema, ex.solutions AS solutions
            """).data()
            statuses = [r["status"] for r in res]
            self.assertTrue(any("Under" in s for s in statuses), "Under Extraction status missing")
            self.assertTrue(any("Over" in s for s in statuses), "Over Extraction status missing")
            self.assertTrue(any("Perfect" in s for s in statuses), "Perfect Extraction status missing")

    def test_06_coffee_species(self):
        """Verify Arabica and Robusta species and varieties."""
        with self.driver.session() as session:
            res = session.run("""
                MATCH (s:Species)
                OPTIONAL MATCH (s)-[:HAS_VARIETY]->(v:Variety)
                RETURN s.name AS name, collect(v.name) AS varieties
            """).data()
            names = [r["name"] for r in res]
            self.assertTrue(any("อาราบิก้า" in n for n in names))
            self.assertTrue(any("โรบัสต้า" in n for n in names))

    def test_07_latte_art_science(self):
        """Verify Latte Art node and techniques."""
        with self.driver.session() as session:
            res = session.run("""
                MATCH (la:LatteArt)-[:HAS_TECHNIQUE]->(t:LatteArtTechnique)
                RETURN la.steaming_temp AS temp, collect(t.name) AS techniques
            """).single()
            self.assertIsNotNone(res)
            self.assertTrue("60" in res["temp"])
            self.assertGreaterEqual(len(res["techniques"]), 2)

if __name__ == "__main__":
    unittest.main(verbosity=2)
