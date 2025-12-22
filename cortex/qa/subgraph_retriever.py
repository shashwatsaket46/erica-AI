from typing import List, Dict
from neo4j import GraphDatabase

class SubgraphRetriever:
    def __init__(self, uri, user, pwd):
        self.driver = GraphDatabase.driver(uri, auth=(user, pwd))

    def close(self):
        self.driver.close()
        
    def get_prereqs(self, concepts: List[str]):
        query = """
        MATCH (c:Concept)
        WHERE c.name IN $concepts
        MATCH (c)-[:PREREQ_OF]->(n:Concept)
        RETURN c.name AS source, n.name AS target
        """
        with self.driver.session() as session:
            result = session.run(query, concepts=concepts)

            nodes = set()
            edges = []

            for row in result:
                source = row["source"]
                target = row["target"]

                nodes.add(source)
                nodes.add(target)

                edges.append({
                    "source": source,
                    "target": target,
                    "type": "PREREQ_OF"
                })

            return {"nodes": list(nodes), "edges": edges}

    def get_siblings(self, concepts: List[str]):
        return []

    def get_examples(self, concepts: List[str]):
        query = """
        MATCH (ex:Example)-[:EXEMPLIFIES]->(c:Concept)
        WHERE c.name IN $concepts
        RETURN ex.id AS id, ex.text AS text
        """
        with self.driver.session() as session:
            return [dict(r) for r in session.run(query, concepts=concepts)]

    def get_resources(self, concepts: List[str]):
        query = """
        MATCH (r:Resource)-[:EXPLAINS]->(c:Concept)
        WHERE c.name IN $concepts
        RETURN r.id AS id, r.type AS type, coalesce(r.span, "") AS span
        """
        with self.driver.session() as session:
            return [dict(r) for r in session.run(query, concepts=concepts)]
        
    def get_summaries(self, concepts: List[str]):
        return []

    def build_subgraph(self, concepts: List[str]) -> Dict:
        prereq_graph = self.get_prereqs(concepts)

        return {
            "concepts": list(concepts),
            "prereq_nodes": list(prereq_graph["nodes"]),
            "prereq_edges": prereq_graph["edges"],
            "siblings": self.get_siblings(concepts),
            "examples": self.get_examples(concepts),
            "resources": self.get_resources(concepts),
            "summaries": self.get_summaries(concepts)
        }
