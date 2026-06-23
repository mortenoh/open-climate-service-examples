"""Start an ingestion as a background job and poll it to completion.

Sending ``Prefer: respond-async`` makes ``/ingestions`` return ``202`` with a job id
instead of blocking. This polls ``/ingestions/jobs/{job_id}`` until the job finishes —
the right pattern for long-running downloads where you don't want one HTTP request held
open for minutes.

Run:
    uv run python examples/04_ingestion/ingest_async_poll.py
"""

from __future__ import annotations

import time
from typing import Any

from ocs_examples import console, http_client

DATASET_ID = "chirps3_precipitation_daily"
START = "2024-01-01"
END = "2024-01-31"
POLL_INTERVAL = 3.0
TERMINAL = {"completed", "succeeded", "failed", "error", "cancelled"}


def main() -> None:
    """Kick off an async ingestion and report status until it settles."""
    payload = {"dataset_id": DATASET_ID, "start": START, "end": END, "overwrite": False, "publish": True}

    with http_client() as client:
        console.section(f"Starting async ingestion of {DATASET_ID}")
        response = client.post("/ingestions", json=payload, headers={"Prefer": "respond-async"})
        response.raise_for_status()
        job: dict[str, Any] = response.json()
        job_id = job.get("job_id") or job.get("id")
        console.info(f"  job id: {job_id}")

        while True:
            status_response = client.get(f"/ingestions/jobs/{job_id}")
            status_response.raise_for_status()
            job = status_response.json()
            status = str(job.get("status", "unknown")).lower()
            console.info(f"  status: {status}")
            if status in TERMINAL:
                break
            time.sleep(POLL_INTERVAL)

        console.section("Final job record")
        console.dump(job)


if __name__ == "__main__":
    main()
