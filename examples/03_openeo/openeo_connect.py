"""Connect with the openEO Python client and list collections.

Open Climate Service speaks openEO, so the standard ``openeo`` client works against it
unchanged. No authentication is required for a local instance.

Needs the openeo extra:
    uv sync --extra openeo

Run:
    uv run python examples/03_openeo/openeo_connect.py
"""

from __future__ import annotations

from ocs_examples import console, openeo_connection


def main() -> None:
    """Connect and print the API version plus the available collections."""
    conn = openeo_connection()
    console.section("Connected")
    console.info(f"  openEO API version: {conn.capabilities().api_version()}")

    collections = conn.list_collections()
    console.section(f"Collections ({len(collections)})")
    for collection in collections:
        print(f"  {collection['id']:<45} {collection.get('title', '')}")


if __name__ == "__main__":
    main()
