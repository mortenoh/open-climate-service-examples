"""Advance a managed dataset forward in time with new upstream data.

``POST /sync/{dataset_id}`` appends the periods reported by the sync plan, extending the
dataset's coverage toward the present. This is what a scheduled job would call
periodically to keep a dataset current.

Run:
    uv run python examples/04_ingestion/sync_forward.py
"""

from __future__ import annotations

from ocs_examples import console, http_client

DATASET_ID = "chirps3_precipitation_daily"
# Optional upper bound; set to None to sync to the latest available upstream data.
END: str | None = None


def main() -> None:
    """Sync a managed dataset forward and publish the new data."""
    payload: dict[str, object] = {"publish": True}
    if END:
        payload["end"] = END

    console.section(f"Syncing {DATASET_ID} forward")
    console.dump(payload)
    with http_client() as client:
        response = client.post(f"/sync/{DATASET_ID}", json=payload, timeout=600.0)
        response.raise_for_status()
        console.section("Sync result")
        console.dump(response.json())


if __name__ == "__main__":
    main()
