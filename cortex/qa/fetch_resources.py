from cortex.graph.neo4j_client import driver

def fetch_resource_chunks(subgraph: dict):
    
    concepts = subgraph.get("concepts", [])
    prereqs = subgraph.get("prerequisites", [])
    siblings = subgraph.get("siblings", [])
    all_concepts = list(set(concepts + prereqs + siblings))

    query = """
    MATCH (c:Concept)
    WHERE c.name IN $concept_list
    OPTIONAL MATCH (c)<-[:EXPLAINS]-(r:Resource)
    RETURN 
        c.name AS concept,
        r.id AS chunk_id,
        r.type AS type,
        r.span AS span
    """

    rows = []
    with driver.session() as session:
        results = session.run(query, concept_list=all_concepts).data()

        for row in results:
            if row["chunk_id"] is None:
                continue

            rows.append({
                "concept": row["concept"],
                "chunk_id": row["chunk_id"],
                "type": row.get("type", ""),
                "span": row.get("span", ""),
            })

    return rows
