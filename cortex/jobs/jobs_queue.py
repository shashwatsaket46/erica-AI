import asyncio
import uuid
from typing import Dict, Any

JOB_QUEUE = asyncio.Queue()
JOBS: Dict[str, Dict[str, Any]] = {}
WORKER_COUNT = 4

# =========================================================================
# JOB WORKER LOOP
# This function defines the worker loop that processes jobs from the queue.
# =========================================================================
async def worker_loop(worker_id: int):
    print(f"[Worker-{worker_id}] Started")
    while True:
        job_id, job_data, job_handler = await JOB_QUEUE.get()

        JOBS[job_id]["status"] = "running"
        JOBS[job_id]["worker"] = worker_id

        try:
            result = await job_handler(job_id, job_data)
            JOBS[job_id]["status"] = "completed"
            JOBS[job_id]["result"] = result

        except Exception as e:
            JOBS[job_id]["status"] = "error"
            JOBS[job_id]["error"] = str(e)

        finally:
            JOB_QUEUE.task_done()


# ==========================================================================
# START WORKERS
# This function starts a specified number of worker tasks in the event loop.
# ==========================================================================
def start_workers(loop: asyncio.AbstractEventLoop):
    for i in range(WORKER_COUNT):
        loop.create_task(worker_loop(i))


# ====================================================
# ENQUEUE JOB
# This function enqueues a new job into the job queue.
# ====================================================
def enqueue_job(job_data: dict, job_handler):
    job_id = str(uuid.uuid4())

    JOBS[job_id] = {
        "status": "queued",
        "result": None,
        "error": None,
        "progress": 0,
        "total": job_data.get("total", 1),
        "worker": None
    }

    JOB_QUEUE.put_nowait((job_id, job_data, job_handler))
    return job_id
