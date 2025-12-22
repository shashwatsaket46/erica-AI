from cortex.llm.llm_client import call_llm
from cortex.semantic.utils import load_prompt
import json

def extract_prerequisites(text, concepts):
    
    prompt = load_prompt("prerequisite_extraction", text)
    prompt = prompt.replace("{{concepts}}", json.dumps(concepts))
    print(f"prompts being sent to LLM Prereq:{prompt}, texts:{text}")

    llm_output = call_llm(prompt)
    
    print("\n========== RAW LLM OUTPUT Prereq==========")
    print(llm_output)
    print("====================================\n")
    prereqs = _normalize_llm_output(llm_output)

    if prereqs:
        return prereqs

    return infer_prereqs_fallback(concepts)


def _normalize_llm_output(result):
    
    if not result:
        return []

    out = []

    if isinstance(result, list):
        for item in result:
            if isinstance(item, dict) and "source" in item and "target" in item:
                if item["source"] != item["target"]:
                    out.append(item)
        return out

    if isinstance(result, str):
        try:
            parsed = json.loads(result)
            return _normalize_llm_output(parsed)
        except:
            return []

    if isinstance(result, dict):
        items = result.get("prerequisites") or []
        return _normalize_llm_output(items)

    return []


def infer_prereqs_fallback(concepts):
    """Minimal fallback: pair simpler → more complex concepts."""
    if not concepts or len(concepts) < 2:
        return []

    ranked = sorted(concepts, key=_complexity_score)

    edges = []
    for i in range(len(ranked) - 1):
        edges.append({
            "source": ranked[i],
            "target": ranked[i+1]
        })
    return edges


def _complexity_score(concept):
    """Estimate concept complexity."""
    technical = ["quantum", "matrix", "thermodynamics", "algorithm", "optimization", "entropy"]
    score = len(concept) + concept.count(" ") * 4
    if any(t in concept.lower() for t in technical):
        score += 10
    return score
