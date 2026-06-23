"""List managed datasets and the ingestion runs that produced them.

Two views of the same lifecycle: ``GET /datasets`` shows the managed datasets currently
available (with their temporal coverage), and ``GET /ingestions`` shows the history of
ingestion runs. Handy for confirming what an instance holds.

Run:
    uv run python examples/04_ingestion/list_ingestions.py
"""

from __future__ import annotations

from typing import Any

from ocs_examples import console, http_client


def main() -> None:
    """Print managed datasets and recent ingestion runs."""
    with http_client() as client:
        datasets: list[dict[str, Any]] = client.get("/datasets").json()
        console.section(f"Managed datasets ({len(datasets)})")
        for dataset in datasets:
            print(f"  {dataset.get('id', '?'):<45} {dataset.get('title', '')}")

        ingestions: list[dict[str, Any]] = client.get("/ingestions").json()
        console.section(f"Ingestion runs ({len(ingestions)})")
        for run in ingestions:
            line = f"  {run.get('dataset_id', '?'):<40} {run.get('status', '')}"
            if run.get("start") or run.get("end"):
                line += f"  {run.get('start', '')} -> {run.get('end', '')}"
            print(line)


if __name__ == "__main__":
    main()
