from cortex.graph.neo4j_client import driver
from neo4j.exceptions import ClientError


# -------------------------------------------
# 1. CREATE GDS PROJECTION
# -------------------------------------------   
def create_gds_projection():
    with driver.session() as session:
        try:
            session.run("CALL gds.graph.drop('neo4j', false)")
        except ClientError as e:
            if "ProcedureNotFound" in str(e) or "Procedure.ProcedureNotFound" in str(e):
                raise RuntimeError("GDS procedures not available on Neo4j instance. Install Graph Data Science plugin or skip clustering.") from e
            else:
                raise
        try:
            session.run("""
            CALL gds.graph.project(
                'neo4j',
                ['Concept'],
                {
                    RELATED: {
                        type: 'RELATED',
                        orientation: 'UNDIRECTED'
                    }
                }
            )
            """)
        except ClientError as e:
            if "ProcedureNotFound" in str(e) or "GDS" in str(e):
                raise RuntimeError("Failed to project GDS graph: procedure not found. Install GDS plugin.") from e
            else:
                raise

# -------------------------------------------
# 2. RUNNING LOUVAIN CLUSTERING using GDS
# -------------------------------------------

def run_louvain():
    try:
        with driver.session() as session:
            res = session.run("""
                CALL gds.louvain.write('neo4j', {
                    writeProperty: 'community'
                })
                YIELD communityCount
                RETURN communityCount
            """).single()
        return {"communities": res["communityCount"]}
    except Exception as e:
        return {"error": "louvain_failed", "message": str(e)}


# -------------------------------------------
# Summarize communities with LLM
# -------------------------------------------

def summarize_communities(ask_llm):

    query = """
    MATCH (c:Concept)
    RETURN c.name AS name, c.community AS community
    ORDER BY community
    """

    with driver.session() as session:
        rows = session.run(query).data()
    clusters = {}
    for row in rows:
        cid = row["community"]
        clusters.setdefault(cid, []).append(row["name"])
    summaries = {}
    for cid, concepts in clusters.items():
        prompt = f"""
Summarize this community of ML concepts:

Concepts: {concepts}

Describe:
- what unifies them
- the level (intro/intermediate/advanced)
- main theme
"""

        summary = ask_llm(prompt)
        summaries[cid] = {
            "concepts": concepts,
            "summary": summary
        }

    return summaries
