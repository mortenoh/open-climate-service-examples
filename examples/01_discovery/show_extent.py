"""Show the spatial extent an instance is configured for.

Each Open Climate Service instance is scoped to one named bounding box, served at
``GET /extent``. The typed client does not wrap this endpoint, so we use the shared
``httpx`` client instead.

Run:
    uv run python examples/01_discovery/show_extent.py
"""

from __future__ import annotations

from ocs_examples import console, http_client


def main() -> None:
    """Fetch and print the configured extent."""
    with http_client() as client:
        response = client.get("/extent")
        response.raise_for_status()
        extent = response.json()

    console.section("Configured extent")
    console.dump(extent)


if __name__ == "__main__":
    main()
