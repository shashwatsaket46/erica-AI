from neo4j import GraphDatabase
import json
import os

from neo4j import GraphDatabase
import json


def safe_load_jsonl(path):
    items = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            try:
                items.append(json.loads(line))
            except:
                continue
    return items


class KGBuilder:

    def __init__(self, uri="bolt://neo4j:7687", user="neo4j", pwd="password"):
        self.driver = GraphDatabase.driver(uri, auth=(user, pwd))

    def close(self):
        self.driver.close()
        


    # --------------------------------------------
    # Constraints needs to be created only once
    # --------------------------------------------
    def create_constraints(self):
        with self.driver.session() as s:
            s.run("CREATE CONSTRAINT IF NOT EXISTS FOR (c:Concept) REQUIRE c.name IS UNIQUE;")
            s.run("CREATE CONSTRAINT IF NOT EXISTS FOR (r:Resource) REQUIRE r.id IS UNIQUE;")
            s.run("CREATE CONSTRAINT IF NOT EXISTS FOR (e:Example) REQUIRE e.id IS UNIQUE;")

    # --------------------------------------------
    # Concepts are the core nodes
    # --------------------------------------------
    def load_concepts(self, path):
        data = safe_load_jsonl(path)

        with self.driver.session() as s:
            for entry in data:
                for c in entry.get("concepts", []):
                    name = c.strip()
                    if name:
                        s.run("MERGE (c:Concept {name:$n})", n=name)

    # --------------------------------------------
    # Definitions are attached to concepts
    # --------------------------------------------
    def load_definitions(self, path):
        data = safe_load_jsonl(path)

        with self.driver.session() as s:
            for entry in data:
                for d in entry.get("definitions", []):

                    if not isinstance(d, dict):
                        continue

                    concept = d.get("concept")
                    definition = d.get("definition")

                    if not concept or not definition:
                        continue

                    s.run("""
                        MATCH (c:Concept {name:$name})
                        SET c.definitions = coalesce(c.definitions, []) + [$definition]
                    """, name=concept, definition=definition)

    # --------------------------------------------
    # Resources are linked to concepts
    # --------------------------------------------
    def load_resources(self, path, filename):
        data = safe_load_jsonl(path)

        with self.driver.session() as s:
            for entry in data:
                chunk = entry.get("chunk_id")
                if not chunk:
                    continue

                rid = f"{filename}/{chunk}"
                r_type = entry.get("type", "pdf")
                span = entry.get("span")

                s.run("""
            MERGE (r:Resource {id:$id})
            SET r.chunk=$chunk, r.type=$type, r.span=$span
        """, id=rid, chunk=chunk, type=r_type, span=span)

                for c in entry.get("concepts", []):
                    s.run("""
                MATCH (r:Resource {id:$rid})
                MATCH (c:Concept {name:$c})
                MERGE (r)-[:EXPLAINS]->(c)
            """, rid=rid, c=c)

    # --------------------------------------------
    # Examples are linked to concepts
    # --------------------------------------------
    def load_examples(self, path, filename):
        data = safe_load_jsonl(path)

        with self.driver.session() as s:
            for entry in data:
                chunk = entry.get("chunk_id")
                if not chunk:
                    continue

                for ex in entry.get("examples", []):

                    if not isinstance(ex, dict):
                        continue

                    concept = ex.get("concept")
                    text = ex.get("example_text")

                    if not concept or not text:
                        continue

                    ex_id = f"{filename}/ex_{chunk}_{hash(text)}"

                    s.run("MERGE (e:Example {id:$id}) SET e.text=$tx",
                          id=ex_id, tx=text)

                    s.run("""
                    MATCH (e:Example {id:$id})
                    MATCH (c:Concept {name:$c})
                    MERGE (e)-[:EXEMPLIFIES]->(c)
                """, id=ex_id, c=concept)

    # --------------------------------------------
    # Prereqs are directed edges between concepts
    # --------------------------------------------
    def load_prereqs(self, path):
            data = safe_load_jsonl(path)
            def normalize(name: str):
                if not name:
                    return None
                return name.strip().lower().replace("-", " ").replace("_", " ")

            with self.driver.session() as s:
                for entry in data:
                    prereqs = entry.get("prerequisites", [])
                    for p in prereqs:
                        if not isinstance(p, dict):
                            continue

                        src = normalize(p.get("source"))
                        tgt = normalize(p.get("target"))

                        if not src or not tgt:
                            continue

                        s.run("""
                            MERGE (a:Concept {name:$src})
                            MERGE (b:Concept {name:$tgt})
                            MERGE (a)-[:PREREQ_OF]->(b)
                        """, src=src, tgt=tgt)



    # --------------------------------------------
    # Related Edges between concepts
    # --------------------------------------------
    def build_related_edges(self):
        with self.driver.session() as s:
            s.run("""
            MATCH (r:Resource)-[:EXPLAINS]->(c1)
            MATCH (r)-[:EXPLAINS]->(c2)
            WHERE c1 <> c2
            MERGE (c1)-[:RELATED]->(c2)
        """)

    # --------------------------------------------
    # Full build process
    # --------------------------------------------
    def build(self, filename):
        semantic = "data/semantic"
        base = filename
        for suf in ("_concepts.jsonl", "_definitions.jsonl", "_prereqs.jsonl", "_examples.jsonl"):
            if base.endswith(suf):
                base = base[:-len(suf)]
                break

        def find(kind: str):
            p1 = os.path.join(semantic, f"{base}_{kind}.jsonl")
            if os.path.exists(p1):
                return p1
            p2 = os.path.join(semantic, f"_{base}_{kind}.jsonl")
            if os.path.exists(p2):
                return p2
            return None

        concepts_path = find("concepts")
        definitions_path = find("definitions")
        prereqs_path = find("prereqs")
        examples_path = find("examples")

        
        used_base = None
        for p in (concepts_path, definitions_path, prereqs_path, examples_path):
            if p:
                name = os.path.basename(p)
                for k in ("_concepts.jsonl", "_definitions.jsonl", "_prereqs.jsonl", "_examples.jsonl"):
                    if name.endswith(k):
                        used_base = name[:-len(k)]
                        break
                if used_base:
                    break
        if not used_base:
            used_base = base

        self.create_constraints()

        if concepts_path:
            self.load_concepts(concepts_path)
        else:
            print(f"Warning: concepts file not found for '{filename}' (tried '{base}_concepts.jsonl' and '_{base}_concepts.jsonl')")

        if definitions_path:
            self.load_definitions(definitions_path)
        else:
            print(f"Warning: definitions file not found for '{filename}'")

        if prereqs_path:
            self.load_prereqs(prereqs_path)
        else:
            print(f"Warning: prereqs file not found for '{filename}'")
        if concepts_path:
            self.load_resources(concepts_path, used_base)
        else:
            print(f"Skipping resources: concepts file not found for '{filename}'")

        if examples_path:
            self.load_examples(examples_path, used_base)
        else:
            print(f"Warning: examples file not found for '{filename}'")

        self.build_related_edges()

        return {"status": "KG built successfully"}


# ==========================================
# EXPORTED FUNCTION TO BUILD KG
# ==========================================
def build_kg(filename: str):
    kg = KGBuilder()
    result = kg.build(filename)
    kg.close()
    return result
