import httpx
import os

async def run_bulk_requests(endpoint: str, files: list[str]):
    BASE_URL = os.getenv("ERICA_API_BASE_URL", "http://localhost:8000")

    results = []
    progress = 0
    total = len(files)

    async with httpx.AsyncClient() as client:
        for f in files:
            payload = {"filename": f}

            r = await client.post(
                BASE_URL.rstrip("/") + endpoint,
                json=payload,
                timeout=600
            )

            results.append({
                "file": f,
                "ok": r.status_code < 300,
                "response": r.json()
            })

            progress += 1

    return {
        "status": "done",
        "progress": progress,
        "total": total,
        "results": results
    }
