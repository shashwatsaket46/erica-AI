from cortex.graph.neo4j_client import driver

def normalize(c):
    if not isinstance(c, str):
        return None
    c = c.replace("_", " ")
    return c.strip().lower()

def fetch_context(concepts: list[str]):
    concepts = [c.lower().strip() for c in concepts]

    query = """
    MATCH (c:Concept)
    WHERE toLower(c.name) IN $concepts
    OPTIONAL MATCH (c)<-[:EXPLAINS]-(r:Resource)
    OPTIONAL MATCH (c)<-[:EXEMPLIFIES]-(e:Example)
    RETURN 
        c.name AS concept,
        c.definitions AS definitions,
        collect(DISTINCT r.id) AS resources,
        collect(DISTINCT e.text) AS examples
    """

    with driver.session() as session:
        rows = session.run(query, concepts=concepts).data()
    normalized_rows = []

    for row in rows:
        normalized_rows.append({
            "concept": row.get("concept", ""),
            "definitions": row.get("definitions") or [],
            "examples": row.get("examples") or [],
            "resources": row.get("resources") or [],
        })
    context_lines = []
    for row in normalized_rows:
        context_lines.append(f"Concept: {row['concept']}")

        for d in row["definitions"]:
            context_lines.append(f"- Definition: {d}")

        for e in row["examples"]:
            context_lines.append(f"- Example: {e}")

        if row["resources"]:
            context_lines.append(f"- Resources: {', '.join(row['resources'])}")

        context_lines.append("")

    return {
        "context": "\n".join(context_lines).strip(),
        "raw_rows": normalized_rows
    }


