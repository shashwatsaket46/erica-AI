import os
import json
from cortex.graph.similarity_graph import cosine_similarity

def load_nodes(node_dir: str):
    nodes = []
    for fname in os.listdir(node_dir):
        if fname.endswith(".json"):
            with open(os.path.join(node_dir, fname), "r", encoding="utf-8") as f:
                nodes.append(json.load(f))
    return nodes


def build_similarity_edges(nodes, top_k=3):
    edges = []

    for i, n1 in enumerate(nodes):
        sims = []
        for j, n2 in enumerate(nodes):
            if i == j:
                continue

            sim = cosine_similarity(n1["embedding"], n2["embedding"])
            sims.append((n2["id"], sim))

        # Sort by similarity score
        sims.sort(key=lambda x: x[1], reverse=True)

        # pick top k edges
        top_neighbors = sims[:top_k]

        for neighbor_id, score in top_neighbors:
            edges.append({
                "source": n1["id"],
                "target": neighbor_id,
                "score": score
            })

    return edges


def save_edges(edges, out_path: str):
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(edges, f, indent=2)
