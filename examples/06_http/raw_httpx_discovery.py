"""Discover an instance using only httpx — no Open Climate Service client.

Everything the typed client does is plain REST, so any HTTP library works. This walks
the STAC catalog (``/stac/catalog.json``) and the openEO collections (``/collections``)
directly, useful as a reference for non-Python consumers.

Run:
    uv run python examples/06_http/raw_httpx_discovery.py
"""

from __future__ import annotations

from typing import Any

from ocs_examples import console, http_client


def main() -> None:
    """Read the STAC catalog and openEO collections over raw HTTP."""
    with http_client() as client:
        catalog: dict[str, Any] = client.get("/stac/catalog.json").json()
        children = [link for link in catalog.get("links", []) if link.get("rel") == "child"]
        console.section(f"STAC catalog children ({len(children)})")
        for link in children:
            print(f"  {link.get('title', link.get('href', '?'))}")

        collections: dict[str, Any] = client.get("/collections").json()
        items = collections.get("collections", [])
        console.section(f"openEO collections ({len(items)})")
        for collection in items:
            print(f"  {collection.get('id', '?'):<45} {collection.get('title', '')}")


if __name__ == "__main__":
    main()
