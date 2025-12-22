import json
import re
from cortex.llm.llm_client import call_llm
from cortex.semantic.utils import load_prompt


# ========================================================================
# CONCEPT EXTRACTOR
# This module provides functions to extract concepts from text using LLMs.
# I am removing some generic concepts from the results to improve quality.
# ========================================================================
def extract_concepts(text: str):
    prompt = load_prompt("concept_extraction", text)
    raw = call_llm(prompt)

    candidates = _parse_concepts(raw)
    if not candidates:
        return []
    text_lower = text.lower()
    filtered = [
        c for c in candidates
        if _fuzzy_contains(text_lower, c.lower())
    ]
    GENERIC = {
        "energy", "interaction", "complexity", "scientific", "mathematical",
        "economic", "philosophical", "academic", "concept", "idea",
        "principle", "field", "entity", "term", "topic", "subject",
        "general concept", "multi-word concept", "general academic concepts"
    }

    filtered = [c for c in filtered if c.lower() not in GENERIC]
    return sorted(set(filtered))


# ========================================================================
# FUZZY CONTAINS
# This helper function checks if a concept is likely present in the text,
# allowing for some fuzziness.
# ========================================================================
def _fuzzy_contains(text_lower: str, concept_lower: str):
    if len(concept_lower) < 3:
        return False
    if concept_lower in text_lower:
        return True
    words = concept_lower.split()
    if all(w in text_lower for w in words if len(w) > 3):
        return True

    return False

# =============================================================================
# PARSE CONCEPTS
# This helper function parses the raw LLM output to extract a list of concepts.
# =============================================================================
def _parse_concepts(raw):
    if not raw:
        return []
    if isinstance(raw, list):
        return [x.strip() for x in raw if isinstance(x, str)]
    if isinstance(raw, str):
        cleaned = (
            raw.replace("```json", "")
               .replace("```", "")
               .replace("JSON:", "")
               .strip()
        )
        try:
            parsed = json.loads(cleaned)
            if isinstance(parsed, list):
                return [x.strip() for x in parsed if isinstance(x, str)]
        except:
            pass
        bullets = re.findall(r"[-•*]\s*(.{2,60})", cleaned)
        if bullets:
            return [b.strip() for b in bullets]
        if "," in cleaned:
            return [x.strip() for x in cleaned.split(",") if x.strip()]
    return []
