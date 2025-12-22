# cortex/qa/pipeline.py

from cortex.llm.concept_extractor import extract_concepts
from cortex.qa.expand_concepts import expand_concepts

from cortex.qa.subgraph_retriever import SubgraphRetriever
from cortex.qa.fetch_resources import fetch_resource_chunks
from cortex.qa.rank_context import rank_context
from cortex.qa.format_context import format_context
from cortex.qa.structured_answer import structured_answer
from cortex.qa.semantic_search import semantic_search
from cortex.llm.llm_client import ask_llm
import re

# =========================================================
# GRAPH RAG PIPELINE
# This pipeline answers user questions by leveraging a Neo4j
# knowledge graph and LLMs in a retrieval-augmented generation (RAG) setup.
# =========================================================
def fallback_keyword_extractor(text: str):
    
    tokens = re.findall(r"[A-Za-z][A-Za-z0-9\-]+", text)
    STOPWORDS = {
        "what", "explain", "describe", "tell", "how", "why",
        "the", "a", "an", "is", "are", "in", "of", "to", "for",
        "and", "on", "give", "me", "about"
    }

    cleaned = [t.lower() for t in tokens if t.lower() not in STOPWORDS]

    return cleaned if cleaned else tokens
subgraph_client = SubgraphRetriever(
    uri="neo4j://neo4j:7687",
    user="neo4j",
    pwd="password"
)

TOP_K = 10


def graph_rag_answer(query: str):
    concepts = extract_concepts(query)
    if not concepts:
        concepts = fallback_keyword_extractor(query)
    expanded = expand_concepts(concepts)
    expanded = list(set(expanded + concepts))
    subgraph = subgraph_client.build_subgraph(expanded)
    resource_rows = fetch_resource_chunks(subgraph)
    if not resource_rows:
        return semantic_fallback_answer(query)
    ranked = rank_context(query, resource_rows, top_k=TOP_K)
    context_text, citations = format_context(ranked)
    answer = structured_answer(
        query=query,
        subgraph=subgraph,
        context=context_text,
        citations=citations,
        ask_llm=ask_llm
    )

    return {
        "concepts": concepts,
        "expanded": expanded,
        "subgraph": subgraph,
        "citations": citations,
        "context_used": context_text,
        "answer": answer
    }
    
def semantic_fallback_answer(query: str):
    top_chunks = semantic_search(query, top_k=5)

    if not top_chunks:
        return {
            "concepts": [],
            "expanded": [],
            "subgraph": {},
            "context_used": "",
            "answer": "No relevant information found in the course material."
        }
    context_text = "\n".join([
        f"[V{i+1}] {chunk['text']}"
        for i, chunk in enumerate(top_chunks)
    ])

    prompt = f"""
Use the following course material to answer the question.

CONTEXT:
{context_text}

QUESTION:
{query}

Provide a clear, correct, concise explanation using only the context above.
"""

    final_answer = ask_llm(prompt)

    return {
        "concepts": [],
        "expanded": [],
        "subgraph": {},
        "context_used": context_text,
        "answer": final_answer
    }