from fastapi import APIRouter
from pydantic import BaseModel
import httpx
import os
import time

router = APIRouter()
BASE_URL = os.getenv("ERICA_API_BASE_URL", "http://localhost:8000")

class PipelineRequest(BaseModel):
    website: list[str] = []
    youtube: list[str] = []
    blogs: list[str] = []
    crawl: list[str] = []
    files: list[str] = []


async def post_json(client, path, payload, timeout=300):
    url = BASE_URL.rstrip("/") + path
    r = await client.post(url, json=payload, timeout=timeout)
    return {
        "ok": r.status_code < 300,
        "status_code": r.status_code,
        "body": r.json()
    }


@router.post("/pipeline/run")
async def pipeline_run(payload: PipelineRequest):
    start = time.time()
    summary = {"errors": [], "ingest_response": None}

    async with httpx.AsyncClient() as client:

        discovered_files = set(payload.files)
        if payload.website or payload.youtube or payload.blogs or payload.crawl:
            ingest_payload = {
                "website": payload.website,
                "youtube": payload.youtube,
                "blogs": payload.blogs,
                "crawl": payload.crawl
            }

            r_ing = await post_json(client, "/ingest", ingest_payload, timeout=600)
            summary["ingest_response"] = r_ing["body"]

            if not r_ing["ok"]:
                summary["errors"].append({"ingest": r_ing["body"]})
                summary["status"] = "failed_in_ingest"
                summary["time_s"] = time.time() - start
                return summary

            for f in r_ing["body"].get("saved_files", []):
                if f.strip():
                    discovered_files.add(f)

        discovered_files = [f for f in discovered_files if f.strip()]
        summary["processed_files"] = discovered_files

        if not discovered_files:
            summary["status"] = "no_input"
            summary["time_s"] = time.time() - start
            return summary
        for filename in discovered_files:
            r = await post_json(client, "/ingest/chunk", {"filename": filename})
            if not r["ok"]:
                summary["errors"].append({"file": filename, "step": "chunk", "error": r["body"]})
                continue
            r = await post_json(client, "/embed", {"filename": filename})
            if not r["ok"]:
                summary["errors"].append({"file": filename, "step": "embed", "error": r["body"]})
                continue
            r = await post_json(client, "/graph/build", {
                "filename": filename,
                "top_k": 3
            })
            if not r["ok"]:
                summary["errors"].append({"file": filename, "step": "graph_build", "error": r["body"]})
                continue
            r = await post_json(client, "/semantic/extract", {"filename": filename})
            if not r["ok"]:
                summary["errors"].append({"file": filename, "step": "semantic_extract", "error": r["body"]})
                continue
            r = await post_json(client, "/kg/build", {"filename": filename})
            if not r["ok"]:
                summary["errors"].append({"file": filename, "step": "kg_build", "error": r["body"]})
                continue
        r_cluster = await post_json(client, "/kg/cluster", {})
        if not r_cluster["ok"]:
            summary["errors"].append({"cluster": r_cluster["body"]})

        r_summary = await post_json(client, "/kg/summarize", {})
        if not r_summary["ok"]:
            summary["errors"].append({"summaries": r_summary["body"]})

    summary["status"] = "finished" if not summary["errors"] else "finished_with_errors"
    summary["time_s"] = time.time() - start
    return summary
