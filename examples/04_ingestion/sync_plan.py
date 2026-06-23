"""Preview how far a managed dataset would advance, without downloading anything.

``GET /sync/{dataset_id}/plan`` is a dry run: it reports the periods that would be
fetched to bring a managed dataset up to date (optionally up to an ``end`` date), so you
can see the work before committing to it. See ``sync_forward.py`` to actually run it.

Run:
    uv run python examples/04_ingestion/sync_plan.py
"""

from __future__ import annotations

from ocs_examples import console, http_client

DATASET_ID = "chirps3_precipitation_daily"
# Optional upper bound; set to None to plan all the way to the latest upstream data.
END: str | None = None


def main() -> None:
    """Fetch and print the sync plan for a managed dataset."""
    params = {"end": END} if END else {}
    console.section(f"Sync plan for {DATASET_ID}")
    with http_client() as client:
        response = client.get(f"/sync/{DATASET_ID}/plan", params=params)
        response.raise_for_status()
        console.dump(response.json())


if __name__ == "__main__":
    main()
