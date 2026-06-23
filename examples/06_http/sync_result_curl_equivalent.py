"""Run a synchronous process graph over raw HTTP — the Python form of the curl example.

The docs show ``POST /result`` with a ``{"process": {"process_graph": {...}}}`` body via
curl. This is the exact equivalent in Python with httpx: build the wrapped payload, post
it, and save the returned bytes. Use it when you can't (or don't want to) add the
Open Climate Service client as a dependency.

Run:
    uv run python examples/06_http/sync_result_curl_equivalent.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ocs_examples import console, http_client

OUTPUT_DIR = Path("output")


def build_payload(collection_id: str) -> dict[str, Any]:
    """Wrap a load -> save_result graph in the ``{"process": {...}}`` envelope."""
    return {
        "process": {
            "process_graph": {
                "load": {
                    "process_id": "load_collection",
                    "arguments": {"id": collection_id, "temporal_extent": None, "spatial_extent": None},
                },
                "save": {
                    "process_id": "save_result",
                    "arguments": {"data": {"from_node": "load"}, "format": "NetCDF"},
                    "result": True,
                },
            }
        }
    }


def main() -> None:
    """Post a process graph to /result and write the bytes to a file."""
    with http_client() as client:
        catalog_links = client.get("/stac/catalog.json").json().get("links", [])
        children = [link for link in catalog_links if link.get("rel") == "child"]
        if not children:
            console.warn("No published datasets. Ingest one first.")
            return
        first = children[0]
        # STAC child links carry an href like /stac/collections/{id}; fall back to it.
        collection_id = str(first.get("id") or first["href"].rstrip("/").split("/")[-1].removesuffix(".json"))
        console.info(f"Using collection {collection_id} ({len(children)} published)")

        console.section("POST /result")
        response = client.post("/result", json=build_payload(collection_id), timeout=600.0)
        response.raise_for_status()

        OUTPUT_DIR.mkdir(exist_ok=True)
        target = OUTPUT_DIR / f"{collection_id}_raw.nc"
        target.write_bytes(response.content)
        console.info(f"  wrote {target} ({len(response.content) / 1_000:.1f} kB)")


if __name__ == "__main__":
    main()
