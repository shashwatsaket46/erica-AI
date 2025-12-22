import os
import json

from cortex.llm.concept_extractor import extract_concepts
from .definition_extractor import extract_definitions
from .prerequisite_extractor import extract_prerequisites
from .example_extractor import extract_examples


def run_semantic_extraction(filename: str):

    chunk_dir = f"data/nodes/{filename}"
    semantic_dir = "data/semantic"
    os.makedirs(semantic_dir, exist_ok=True)
    concept_out = open(f"{semantic_dir}/{filename}_concepts.jsonl", "w", encoding="utf-8")
    definition_out = open(f"{semantic_dir}/{filename}_definitions.jsonl", "w", encoding="utf-8")
    prereq_out = open(f"{semantic_dir}/{filename}_prereqs.jsonl", "w", encoding="utf-8")
    example_out = open(f"{semantic_dir}/{filename}_examples.jsonl", "w", encoding="utf-8")
    files = sorted(os.listdir(chunk_dir))
    for fname in files:
        if not fname.endswith(".json"):
            continue

        path = f"{chunk_dir}/{fname}"
        chunk = json.load(open(path, "r", encoding="utf-8"))
        text = chunk.get("content", "")
        chunk_id = fname.replace(".json", "")
        concepts = extract_concepts(text)
        definitions = extract_definitions(text)
        prereqs = extract_prerequisites(text,concepts)
        examples = extract_examples(text)
        concept_out.write(json.dumps({
            "chunk_id": chunk_id,
            "concepts": concepts
        }) + "\n")

        definition_out.write(json.dumps({
            "chunk_id": chunk_id,
            "definitions": definitions
        }) + "\n")
        prereq_out.write(json.dumps({
            "chunk_id": chunk_id,
            "prerequisites": prereqs
        }) + "\n")
        example_out.write(json.dumps({
            "chunk_id": chunk_id,
            "examples": examples
        }) + "\n")

        print(f"Processed {chunk_id}")

    concept_out.close()
    definition_out.close()
    prereq_out.close()
    example_out.close()

    return {
        "message": "Semantic extraction completed",
        "chunks_processed": len(files),
        "outputs": {
            "concepts": f"{semantic_dir}/{filename}_concepts.jsonl",
            "definitions": f"{semantic_dir}/{filename}_definitions.jsonl",
            "prereqs": f"{semantic_dir}/{filename}_prereqs.jsonl",
            "examples": f"{semantic_dir}/{filename}_examples.jsonl"
        }
    }
