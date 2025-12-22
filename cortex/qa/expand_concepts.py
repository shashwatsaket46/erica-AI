from neo4j import GraphDatabase

# =========================================================
# EXPAND CONCEPTS
# This module expands a list of ML concepts by finding related concepts
# in the Neo4j knowledge graph.
# =========================================================
STOPWORDS = {
    "technical", "math", "data", "information", "coding", "programming",
    "concept", "example", "lesson", "chapter", "learning", "practice"
}

def expand_concepts(concepts):
    uri = "neo4j://neo4j:7687"
    auth = ("neo4j", "password")
    driver = GraphDatabase.driver(uri, auth=auth)

    expanded = set()

    with driver.session() as session:
        for c in concepts:

            clean = c.lower().strip()
            if clean in STOPWORDS:
                continue
            exists = session.run("""
                MATCH (n:Concept)
                WHERE toLower(n.name) = toLower($c)
                RETURN n.name AS name
            """, c=c).single()

            if not exists:
                continue
            canonical = exists["name"]
            expanded.add(canonical)
            neigh = session.run("""
                MATCH (n:Concept)
                WHERE toLower(n.name) = toLower($c)
                OPTIONAL MATCH (n)-[:RELATED|PREREQ_OF]-(m:Concept)
                RETURN collect(DISTINCT m.name) AS neighbors
            """, c=c).single()

            for nb in neigh["neighbors"]:
                if nb and nb.lower() not in STOPWORDS:
                    expanded.add(nb)

    return list(expanded)
