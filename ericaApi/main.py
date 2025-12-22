# ============================
#   Erica API Main File
# ============================

from fastapi import FastAPI, APIRouter, HTTPException
from pydantic import BaseModel
import os
import json
import requests
import asyncio

# Cortex imports
from cortex.ingest.website_loader import load_website
from cortex.ingest.youtube_loader import load_youtube
from cortex.ingest.blog_loader import load_blog
from cortex.ingest.utils import save_text, sanitize_filename
from cortex.crawler.link_crawler import crawl_website

from cortex.chunk.paragraph_chunk import paragraph_chunk
from cortex.embed.embedder import embed_text
from cortex.graph.edge_builder import load_nodes, build_similarity_edges, save_edges
from cortex.semantic.run_semantic_extractor import run_semantic_extraction
from cortex.graph.kg_builder import build_kg
from cortex.graph.cluster_graph import (
    create_gds_projection,
    run_louvain,
    summarize_communities,
)
from cortex.llm.llm_client import ask_llm
from cortex.qa.pipeline import graph_rag_answer
from cortex.qa.subgraph_retriever import SubgraphRetriever
from cortex.pipeline.pipeline_router import router as pipeline_router
from cortex.bulk.bulk_executor import run_bulk_requests
from cortex.jobs.jobs_queue import enqueue_job, JOBS, start_workers
from cortex.jobs.bulk_job_handler import bulk_job_handler

from fastapi.middleware.cors import CORSMiddleware


# =============================================
# CONFIG
# =============================================
app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
DATA_DIR = "data/raw"
NODES_DIR = "data/nodes"
GRAPH_DIR = "data/graph"

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(NODES_DIR, exist_ok=True)
os.makedirs(GRAPH_DIR, exist_ok=True)

OLLAMA = os.getenv("OLLAMA_HOST", "http://host.docker.internal:11434")

NEO4J_URI = os.getenv("NEO4J_URI", "neo4j://neo4j:7687")
NEO4J_USER = os.getenv("NEO4J_USER", "neo4j")
NEO4J_PASSWORD = os.getenv("NEO4J_PASSWORD", "password")

subgraph = SubgraphRetriever(NEO4J_URI, NEO4J_USER, NEO4J_PASSWORD)

# ============================================================
# Helper — FILE SEARCH (FULL FILENAME INCLUDING .txt)
# ============================================================

class IngestRequest(BaseModel):
    website: list[str] = []
    youtube: list[str] = []
    blogs: list[str] = []
    crawl: list[str] = []

class ChunkRequest(BaseModel):
    filename: str 
    
class EmbedRequest(BaseModel):
    filename: str
    
class GraphBuildRequest(BaseModel):
    filename: str
    top_k: int = 3
    
class SemanticRequest(BaseModel):
    filename: str

class KGReq(BaseModel):
    filename: str

class AskRequest(BaseModel):
    question: str   

class GenericBulkRequest(BaseModel):
    endpoint: str
    payload_key: str
    files: list[str]
class BulkJobPayload(BaseModel):
    files: list[str]
    endpoint: str
    
def find_raw_file(full_filename: str) -> str:
    """
    Search recursively inside data/raw for the EXACT file:
        pantelis_github_io_about_html.txt
    """
    for root, dirs, files in os.walk(DATA_DIR):
        if full_filename in files:
            return os.path.join(root, full_filename)

    raise FileNotFoundError(f"{full_filename} not found inside data/raw/")

def run_thread(fn, *args, **kwargs):
    return asyncio.to_thread(fn, *args, **kwargs)

# ============================================================
# ROUTES
# ============================================================

@app.get("/",tags=["Check API"])
def root():
    return {"message": "Erica API running"}

@app.get("/llm-test",tags=["Check LLM Connection"])
def llm_test():
    try:
        r = requests.post(
            f"{OLLAMA}/api/generate",
            json={"model": "qwen2.5:3b", "prompt": "Hello", "stream": False},
            timeout=10,
        )
        return r.json()
    except Exception as e:
        return {"error": str(e)}

# ============================================================
# INGEST (WEB / YT / BLOG / CRAWLER)
# ============================================================



@app.post("/ingest", tags=["Ingest"])
def ingest_sources(payload: IngestRequest):

    saved_files = []
    stats = dict(websites=0, youtube=0, blogs=0, crawled=0, total_saved=0)

    # Websites ingestion
    for url in payload.website:
        text = load_website(url)
        if text:
            fname = sanitize_filename(url)
            save_text(f"{DATA_DIR}/websites", fname, text)
            saved_files.append(fname + ".txt")
            stats["websites"] += 1

    # YouTube ingestion
    for url in payload.youtube:
        text = load_youtube(url)
        if text:
            fname = sanitize_filename(url)
            save_text(f"{DATA_DIR}/youtube", fname, text)
            saved_files.append(fname + ".txt")
            stats["youtube"] += 1

    # Blogs ingestion
    for url in payload.blogs:
        text = load_blog(url)
        if text:
            fname = sanitize_filename(url)
            save_text(f"{DATA_DIR}/blogs", fname, text)
            saved_files.append(fname + ".txt")
            stats["blogs"] += 1

    # Crawler ingestion
    for seed in payload.crawl:
        for link in crawl_website(seed, max_depth=4):
            text = load_website(link)
            if text:
                fname = sanitize_filename(link)
                save_text(f"{DATA_DIR}/websites", fname, text)
                saved_files.append(fname + ".txt")
                stats["crawled"] += 1

    stats["total_saved"] = len(saved_files)

    return {
        "ok": True,
        "saved_files": saved_files,
        "stats": stats
    }

# ============================================================
# CHUNK
# ============================================================

# FULL filename including ".txt"

@app.post("/ingest/chunk", tags=["Chunking"])
async def chunk_file(req: ChunkRequest):
    full_filename = req.filename  # e.g. pantelis_github_io_about_html.txt

    try:
        raw_path = find_raw_file(full_filename)
    except FileNotFoundError as e:
        return {"ok": False, "error": str(e)}

    raw = await run_thread(lambda: open(raw_path, "r", encoding="utf-8").read())
    chunks = await run_thread(paragraph_chunk, raw)

    # Always sanitize node folder name
    folder_name = sanitize_filename(full_filename.replace(".txt", ""))
    node_dir = os.path.join(NODES_DIR, folder_name)
    os.makedirs(node_dir, exist_ok=True)

    node_files = []

    # Save chunk files
    for i, chunk in enumerate(chunks):
        node = {
            "id": f"{folder_name}_chunk_{i}",
            "source": folder_name,
            "order": i,
            "content": chunk,
        }

        node_path = os.path.join(node_dir, f"{node['id']}.json")
        await run_thread(lambda p, d: open(p, "w").write(json.dumps(d, indent=2)), node_path, node)

        node_files.append(node_path)

    return {
        "ok": True,
        "chunks": len(chunks),
        "node_dir": folder_name,
        "node_files": node_files,
    }

# ============================================================
# EMBED (Update SAME files)
# ============================================================

@app.post("/embed", tags=["Embedding"])
async def embed_nodes(req: EmbedRequest):
    folder_name = sanitize_filename(req.filename.replace(".txt", ""))
    node_dir = os.path.join(NODES_DIR, folder_name)

    if not os.path.exists(node_dir):
        return {"ok": False, "error": f"directory not found: {node_dir}"}
    nodes = load_nodes(node_dir)

    updated_paths = []

    for node in nodes:
        content = node.get("content", "")
        emb = embed_text(content)
        node["embedding"] = emb
        path = os.path.join(node_dir, f"{node['id']}.json")

        with open(path, "w", encoding="utf-8") as f:
            json.dump(node, f, indent=2)

        updated_paths.append(path)

    return {
        "ok": True,
        "updated": len(updated_paths),
        "updated_files": updated_paths
    }
# ============================================================
# GRAPH BUILD
# ============================================================



@app.post("/graph/build", tags=["Graph Build"])
def build_graph(req: GraphBuildRequest):

    folder_name = sanitize_filename(req.filename.replace(".txt", ""))
    node_dir = os.path.join(NODES_DIR, folder_name)

    if not os.path.exists(node_dir):
        return {"ok": False, "error": f"missing node dir: {node_dir}"}

    nodes = load_nodes(node_dir)
    edges = build_similarity_edges(nodes, top_k=req.top_k)

    edge_path = os.path.join(GRAPH_DIR, f"{folder_name}_graph.json")
    save_edges(edges, edge_path)

    return {
        "ok": True,
        "nodes": len(nodes),
        "edges": len(edges),
        "saved_to": edge_path,
    }

# ============================================================
# SEMANTIC EXTRACT
# ============================================================



@app.post("/semantic/extract", tags=["Semantic Extract"])
def semantic_extract(req: SemanticRequest):
    try:
        # Convert raw filename → node folder name
        folder_name = sanitize_filename(req.filename.replace(".txt", ""))

        return {
            "ok": True,
            "result": run_semantic_extraction(folder_name)
        }

    except Exception as e:
        return {"ok": False, "error": str(e)}



# ============================================================
# KG Building
# ============================================================



@app.post("/kg/build", tags=["KG Build"])
def kg_build(req: KGReq):
    try:
        
        return build_kg(req.filename)
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ============================================================
# KG CLUSTER + SUMMARIZE
# ============================================================
@app.post("/kg/cluster", tags=["KG Cluster"])
def kg_cluster():
    try:
        create_gds_projection()
        lou = run_louvain()
        if "error" in lou:
            return {"ok": False, "louvain": lou}
        return {"ok": True, "summaries": summarize_communities(ask_llm)}
    except Exception as e:
        return {"ok": False, "error": str(e)}

# ============================================================
# KG SUMMARIZE
# ============================================================
@app.post("/kg/summarize", tags=["KG Summarize"])
def kg_summarize():
    return summarize_communities(ask_llm)

# ============================================================
# RAG
# ============================================================



@app.post("/ask", tags=["RAG QA"])
def ask(req: AskRequest):
    return graph_rag_answer(req.question)

# ============================================================
# Subgraph
# ============================================================

@app.post("/kg/subgraph", tags=["KG Subgraph"])
def build_subgraph(payload: dict):
    concepts = payload.get("concepts", [])
    if isinstance(concepts, str):
        concepts = [concepts]
    if not isinstance(concepts, list):
        raise ValueError("concepts must be a list of strings")

    return subgraph.build_subgraph(concepts)


# ============================================================
# Including the pipeline router
# ============================================================


app.include_router(pipeline_router)

@app.post("/bulk/run", tags=["Bulk Run"])
async def bulk_run(req: GenericBulkRequest):
    return await run_bulk_requests(
        endpoint=req.endpoint,
        files=req.files
    )
    

# ============================================================
# JOB QUEUE AND WORKERS
# ============================================================

@app.on_event("startup")
async def startup_event():
    loop = asyncio.get_event_loop()
    start_workers(loop)
    print("Workers started")

# ============================================================
# JOB ROUTES                                                    
# ============================================================

@app.post("/job/submit", tags=["Job Submit"])
def submit_bulk_job(payload: BulkJobPayload):
    job_data = {
        "files": payload.files,
        "endpoint": payload.endpoint,
        "total": len(payload.files)
    }
    job_id = enqueue_job(job_data, bulk_job_handler)
    return {"job_id": job_id, "status": "queued"}


# ============================================================
# JOB STATUS AND RESULT ROUTES
# ============================================================

@app.get("/job/status/{job_id}", tags=["Job Status"])
def job_status(job_id: str):
    if job_id not in JOBS:
        return {"error": "invalid job id"}

    return JOBS[job_id]

# ============================================================
# JOB RESULT ROUTE
# ============================================================
@app.get("/job/result/{job_id}", tags=["Job Result"])
def job_result(job_id: str):
    job = JOBS.get(job_id)
    if not job:
        return {"error": "invalid job id"}

    if job["status"] != "completed":
        return {"error": "job not completed", "status": job["status"]}

    return job["result"]





