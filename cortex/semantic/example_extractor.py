from cortex.llm.llm_client import call_llm
from .utils import load_prompt

def extract_examples(text: str):
    prompt = load_prompt("example_extraction", text)
    result = call_llm(prompt)
    if not result:
        return []

    normalized = []
    for item in result:
        if (
                isinstance(item, dict)
                and "concept" in item
                and "example_text" in item
                and isinstance(item["concept"], str)
                and isinstance(item["example_text"], str)
        ):
            normalized.append(item)

    return normalized
