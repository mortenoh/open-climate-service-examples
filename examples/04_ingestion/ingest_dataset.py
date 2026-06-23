"""Ingest a dataset template into a managed dataset (synchronous).

Posts to ``/ingestions`` to download a template (CHIRPS, WorldPop, ...) for the
instance's configured extent over a date range, build its GeoZarr store, and publish it
so it shows up under ``/datasets`` and the STAC catalog. Runs synchronously and waits
for completion; see ``ingest_async_poll.py`` for the background-job variant.

Run:
    uv run python examples/04_ingestion/ingest_dataset.py
"""

from __future__ import annotations

from ocs_examples import console, http_client

# A template id from `GET /dataset-templates` (see list_dataset_templates.py).
DATASET_ID = "chirps3_precipitation_daily"
START = "2024-01-01"
END = "2024-01-31"


def main() -> None:
    """Ingest a one-month CHIRPS slice and publish it."""
    payload = {
        "dataset_id": DATASET_ID,
        "start": START,
        "end": END,
        "overwrite": False,
        "publish": True,
    }
    console.section(f"Ingesting {DATASET_ID}  {START} -> {END}")
    console.dump(payload)

    with http_client() as client:
        response = client.post("/ingestions", json=payload, timeout=600.0)
        response.raise_for_status()
        console.section("Ingestion result")
        console.dump(response.json())


if __name__ == "__main__":
    main()
