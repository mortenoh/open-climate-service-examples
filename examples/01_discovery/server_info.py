"""Check an instance's health and report its version and openEO capabilities.

Combines three unauthenticated endpoints: ``GET /health`` (liveness), ``GET /info``
(version and environment), and ``GET /.well-known/openeo`` (advertised openEO API
versions). A quick first call to confirm an instance is up before running other examples.

Run:
    uv run python examples/01_discovery/server_info.py
"""

from __future__ import annotations

from ocs_examples import console, http_client


def main() -> None:
    """Print health, version info, and advertised openEO versions."""
    with http_client() as client:
        health = client.get("/health")
        console.section("Health")
        console.info(f"  {health.status_code} {health.json()}")

        info = client.get("/info")
        if info.is_success:
            console.section("Info")
            console.dump(info.json())

        openeo = client.get("/.well-known/openeo")
        if openeo.is_success:
            console.section("openEO versions")
            console.dump(openeo.json())


if __name__ == "__main__":
    main()
