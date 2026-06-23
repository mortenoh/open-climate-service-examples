"""Execute a process graph synchronously with the typed client (no openeo client needed).

Builds a ``load_collection`` -> ``save_result`` graph from the typed models in
``ocs_examples.graphs`` and runs it via ``service.execute`` (``POST /result``), writing
the bytes straight to a local file. This is the lightweight path when you don't want the
full openEO client.

Run:
    uv run python examples/03_openeo/sync_result_raw_graph.py
"""

from __future__ import annotations

from pathlib import Path

from ocs_examples import (
    SaveFormat,
    TemporalExtent,
    climate_service,
    console,
    dataset_id_of,
    first_published_dataset,
)
from ocs_examples.graphs import load_and_save_graph

OUTPUT_DIR = Path("output")


def main() -> None:
    """Run a load -> save graph synchronously and store the NetCDF result."""
    with climate_service() as service:
        dataset = first_published_dataset(service)
        if dataset is None:
            return
        dataset_id = dataset_id_of(dataset)

        # Use the dataset's own temporal coverage as the window.
        ds = service.open_dataset(dataset_id)
        temporal = TemporalExtent(
            start=str(ds["t"].values[0])[:10],
            end=str(ds["t"].values[min(ds.sizes["t"] - 1, 10)])[:10],
        )

        graph = load_and_save_graph(dataset_id, temporal, save_format=SaveFormat.NETCDF)
        console.section("Process graph")
        console.dump(graph.to_payload())

        OUTPUT_DIR.mkdir(exist_ok=True)
        target = OUTPUT_DIR / f"{dataset_id}_result.nc"
        console.section("Executing POST /result")
        result = service.execute(graph.to_payload(), path=target)
        console.info(f"  wrote {result}")


if __name__ == "__main__":
    main()
