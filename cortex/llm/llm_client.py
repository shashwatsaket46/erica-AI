import os
import json
import requests

OLLAMA = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")

#=======================================================================
# LLM CLIENT
# This module provides functions to interact with the LLM service.
#=======================================================================
def call_llm(prompt: str, model="qwen2.5:3b"):
    response = requests.post(
        f"{OLLAMA}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False},
        timeout=60
    )
    text = response.json().get("response", "")
    try:
        return json.loads(text)
    except:
        try:
            start = text.index("[")
            end = text.rindex("]") + 1
            return json.loads(text[start:end])
        except:
            return []


#===========================================================================
# ASK LLM
# This function sends a prompt to the LLM and returns the raw text response.
#===========================================================================
def ask_llm(prompt: str, model: str = "qwen2.5:3b"):
    response = requests.post(
        f"{OLLAMA}/api/generate",
        json={"model": model, "prompt": prompt, "stream": False}
    )
    return response.json().get("response", "")