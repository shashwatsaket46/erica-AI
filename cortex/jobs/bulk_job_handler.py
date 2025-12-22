from cortex.bulk.bulk_executor import run_bulk_requests
from cortex.jobs.jobs_queue import JOBS

# ==========================================
# BULK JOB HANDLER
# This function handles bulk jobs by processing files through a specified endpoint.
# ==========================================
async def bulk_job_handler(job_id: str, job_data: dict):
    files = job_data["files"]
    endpoint = job_data["endpoint"]

    JOBS[job_id]["total"] = len(files)
    JOBS[job_id]["progress"] = 0
    results = []
    for idx, filename in enumerate(files):
        payload = {"filename": filename}
        r = await run_bulk_requests(
            endpoint=endpoint,
            files=[filename]
        )

        results.append({filename: r})

        JOBS[job_id]["progress"] = idx + 1

    return results