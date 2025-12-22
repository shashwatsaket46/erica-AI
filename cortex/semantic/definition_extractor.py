import json
from cortex.llm.llm_client import call_llm
from cortex.semantic.utils import load_prompt

def extract_definitions(text: str):
    if len(text.strip()) < 30:
        return []

    prompt = load_prompt("definition_extraction", text)
    print(f"prompts being sent to LLM Definition:{prompt}, texts:{text}")
    
    raw = call_llm(prompt)
    print("\n========== RAW LLM OUTPUT ==========")
    print(raw)
    print("====================================\n")

    if not raw:
        return []

    if isinstance(raw, str):
        try:
            raw = json.loads(raw)
        except:
            return []

    if not isinstance(raw, list):
        return []

    cleaned = []
    for item in raw:
        if not isinstance(item, dict):
            continue

        concept = item.get("concept", "").strip()
        definition = item.get("definition", "").strip()

        if concept.lower().startswith("a definition means"):
            continue
        if concept.lower() in ("definition", "rewrite unclear definitions"):
            continue
        if "a definition means" in definition.lower():
            continue

        if concept and definition:
            cleaned.append({"concept": concept, "definition": definition})

    return cleaned




