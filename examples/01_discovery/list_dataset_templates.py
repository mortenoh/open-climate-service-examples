"""List the dataset templates an instance can ingest.

Templates (``GET /dataset-templates``) are the blueprints — CHIRPS, ERA5-Land,
WorldPop, ... — that you ingest into managed datasets for the configured extent. This
tells you what is available to pass to the ingestion examples.

Run:
    uv run python examples/01_discovery/list_dataset_templates.py
"""

from __future__ import annotations

from typing import Any

from ocs_examples import console, http_client


def main() -> None:
    """Print every available dataset template id and its description."""
    with http_client() as client:
        response = client.get("/dataset-templates")
        response.raise_for_status()
        templates: list[dict[str, Any]] = response.json()

    console.section(f"Dataset templates ({len(templates)})")
    for template in templates:
        template_id = template.get("id", "?")
        description = template.get("description") or template.get("title") or ""
        print(f"  {template_id:<40} {description}")


if __name__ == "__main__":
    main()
