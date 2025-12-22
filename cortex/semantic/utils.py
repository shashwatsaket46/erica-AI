import json
import os

PROMPTS_PATH = os.path.join(os.path.dirname(__file__), "prompts.json")

def load_prompt(key: str, text: str):
    with open(PROMPTS_PATH, "r", encoding="utf-8") as f:
        prompts = json.load(f)

    if key not in prompts:
        raise ValueError(f"Prompt '{key}' not found in prompts.json")

    prompt = prompts[key]

    if not isinstance(prompt, str):
        raise ValueError(f"Prompt '{key}' must be a string.")

    return prompt.replace("{{text}}", text)


