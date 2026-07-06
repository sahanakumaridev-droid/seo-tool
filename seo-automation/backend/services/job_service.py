"""
job_service.py
In-memory async job queue for bulk operations.
Handles bulk content generation, bulk WP publishing with progress tracking.
For production scale, swap with Celery + Redis.
"""
import asyncio
import uuid
from datetime import datetime, timezone
from typing import Dict, Any, Callable, Coroutine
from models.schemas import JobStatus

# In-memory job store
_jobs: Dict[str, JobStatus] = {}


def create_job(total: int) -> str:
    job_id = str(uuid.uuid4())
    _jobs[job_id] = JobStatus(
        job_id=job_id,
        status="pending",
        total=total,
        completed=0,
        failed=0,
        results=[],
        created_at=datetime.now(timezone.utc),
        updated_at=datetime.now(timezone.utc),
    )
    return job_id


def get_job(job_id: str) -> JobStatus | None:
    return _jobs.get(job_id)


def update_job(job_id: str, **kwargs):
    job = _jobs.get(job_id)
    if job:
        for k, v in kwargs.items():
            setattr(job, k, v)
        job.updated_at = datetime.now(timezone.utc)


async def run_bulk_job(
    job_id: str,
    items: list,
    task_fn: Callable[..., Coroutine],
    concurrency: int = 3,
    retry_count: int = 2,
):
    """
    Run a bulk job with concurrency control and retry logic.
    task_fn receives each item and returns a dict result.
    """
    update_job(job_id, status="running")
    semaphore = asyncio.Semaphore(concurrency)

    async def process_item(item):
        async with semaphore:
            for attempt in range(retry_count + 1):
                try:
                    result = await task_fn(item)
                    job = _jobs.get(job_id)
                    if job:
                        job.completed += 1
                        job.results.append(result)
                        job.updated_at = datetime.now(timezone.utc)
                    return result
                except Exception as e:
                    if attempt == retry_count:
                        job = _jobs.get(job_id)
                        if job:
                            job.failed += 1
                            job.results.append({"error": str(e), "item": str(item)[:100]})
                            job.updated_at = datetime.now(timezone.utc)
                    else:
                        await asyncio.sleep(1 * (attempt + 1))  # backoff

    await asyncio.gather(*[process_item(item) for item in items])
    job = _jobs.get(job_id)
    if job:
        job.status = "done" if job.failed == 0 else "partial"
        job.updated_at = datetime.now(timezone.utc)


def cleanup_old_jobs(max_jobs: int = 100):
    """Keep only the most recent N jobs in memory."""
    if len(_jobs) > max_jobs:
        sorted_ids = sorted(_jobs.keys(), key=lambda jid: _jobs[jid].created_at or datetime.min)
        for jid in sorted_ids[:len(_jobs) - max_jobs]:
            del _jobs[jid]
