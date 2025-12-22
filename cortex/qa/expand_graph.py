from neo4j import GraphDatabase
from cortex.graph.neo4j_client import driver

# =========================================================
# EXPAND CONCEPTS
# This module expands a list of ML concepts by finding related concepts
# in the Neo4j knowledge graph.
# =========================================================
def expand_concepts(concepts):
    expanded = set(concepts)
    with driver.session() as session:
        for c in concepts:
            query = """
            MATCH (n:Concept {name:$c})-[:RELATED|PREREQ_OF]-(m)
            RETURN m.name AS name
            """
            rows = session.run(query, c=c).data()

            for r in rows:
                expanded.add(r["name"])

    return list(expanded)
