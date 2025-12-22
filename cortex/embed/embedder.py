import requests
import os

OLLAMA = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")

def embed_text(text: str, model: str = "qwen2.5:3b") -> list:
    """
    Generate embeddings using Ollama embedding API.
    """
    response = requests.post(
        f"{OLLAMA}/api/embeddings",
        json={"model": model, "prompt": text}
    )

    data = response.json()

    if "embedding" not in data:
        raise ValueError(f"Embedding error: {data}")

    return data["embedding"]
