from chromadb import PersistentClient
import requests
import os

OLLAMA = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")
client = PersistentClient(path="chroma_store")
collection = client.get_or_create_collection(name="course_chunks")

# =======================================================================
# EMBEDDING AND SEMANTIC SEARCH
# These functions handle text embedding and semantic search using Ollama.
# =======================================================================
def embed_text(text: str, model: str = "nomic-embed-text"):
    response = requests.post(
        f"{OLLAMA}/api/embeddings",
        json={"model": model, "prompt": text},
        timeout=60
    )
    data = response.json()

    if "embedding" not in data:
        raise RuntimeError(f"Ollama embedding failed: {data}")

    return data["embedding"]

# =======================================================================
# CHROMA DB INTERACTIONS
# These functions manage adding chunks and performing semantic search.
# =======================================================================
def add_chunk(chunk_id: str, text: str):
    emb = embed_text(text)
    collection.add(ids=[chunk_id], documents=[text], embeddings=[emb])
    
# =======================================================================
# SEMANTIC SEARCH
# This function performs semantic search over the stored chunks.
# =======================================================================
def semantic_search(query: str, top_k: int = 5):
    q_emb = embed_text(query)

    results = collection.query(
        query_embeddings=[q_emb],
        n_results=top_k
    )

    docs = results.get("documents", [[]])[0]
    ids = results.get("ids", [[]])[0]
    distances = results.get("distances", [[]])[0]

    return [
        {
            "id": cid,
            "text": text,
            "score": 1 - dist
        }
        for text, cid, dist in zip(docs, ids, distances)
    ]
