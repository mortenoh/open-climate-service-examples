"""Run a load -> apply -> reduce pipeline as an openEO batch job.

The canonical openEO workflow: connect, ``load_collection`` over a spatial/temporal
window, apply an element-wise transform, reduce the time dimension, then submit it as a
batch job and wait for the result assets. Uses the first collection's own advertised
extent so it runs against whatever is published.

Needs the openeo extra:
    uv sync --extra openeo

Run:
    uv run python examples/03_openeo/openeo_batch_job.py
"""

from __future__ import annotations

from ocs_examples import console, openeo_connection


def main() -> None:
    """Submit a max-over-time batch job and print its result assets."""
    conn = openeo_connection()
    collections = conn.list_collections()
    if not collections:
        console.warn("No published collections. Ingest one first.")
        return

    collection = collections[0]
    west, south, east, north = collection["extent"]["spatial"]["bbox"][0]
    temporal_extent = collection["extent"]["temporal"]["interval"][0]
    console.section(f"Collection {collection['id']}")
    console.info(f"  spatial:  {west:.2f}, {south:.2f}  ->  {east:.2f}, {north:.2f}")
    console.info(f"  temporal: {temporal_extent[0]}  ->  {temporal_extent[1]}")

    cube = conn.load_collection(
        collection["id"],
        spatial_extent={"west": west, "south": south, "east": east, "north": north},
        temporal_extent=temporal_extent,
    )
    cube = cube.apply(lambda x: x).max_time()

    console.section("Submitting batch job")
    job = cube.create_job(title="max-time-demo", format="GTiff")
    console.info(f"  job id: {job.job_id}")
    job.start_and_wait()

    assets = job.get_results().get_assets()
    console.section(f"Result assets ({len(assets)})")
    for asset in assets:
        print(f"  {asset.name}: {asset.href}")


if __name__ == "__main__":
    main()
