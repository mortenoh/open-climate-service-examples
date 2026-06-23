"""Store a reusable user-defined process (UDP) and then invoke it.

A UDP is a parameterised process graph saved on the instance (``PUT /process_graphs/{id}``)
that you can call by name from later graphs — the openEO equivalent of the stored
workflows under ``service.workflows()``. This stores one that scales a collection by a
parameter, then runs it via ``POST /result``.

Run:
    uv run python examples/03_openeo/store_and_run_udp.py
"""

from __future__ import annotations

from pathlib import Path
from typing import Any

from ocs_examples import (
    climate_service,
    console,
    dataset_id_of,
    first_published_dataset,
    http_client,
)

UDP_ID = "ocs_examples_scale"
OUTPUT_DIR = Path("output")


def udp_definition(dataset_id: str) -> dict[str, Any]:
    """Return a UDP that loads ``dataset_id`` and divides it by a ``divisor`` parameter."""
    return {
        "summary": "Load a collection and divide it by a parameter (examples UDP)",
        "parameters": [
            {"name": "divisor", "description": "Value to divide by", "schema": {"type": "number"}},
        ],
        "process_graph": {
            "load": {
                "process_id": "load_collection",
                "arguments": {"id": dataset_id, "temporal_extent": None, "spatial_extent": None},
            },
            "scale": {
                "process_id": "apply",
                "arguments": {
                    "data": {"from_node": "load"},
                    "process": {
                        "process_graph": {
                            "div": {
                                "process_id": "divide",
                                "arguments": {"x": {"from_parameter": "x"}, "y": {"from_parameter": "divisor"}},
                                "result": True,
                            }
                        }
                    },
                },
                "result": True,
            },
        },
    }


def main() -> None:
    """Store the UDP, confirm it is listed, then run it."""
    with climate_service() as service:
        dataset = first_published_dataset(service)
        if dataset is None:
            return
        dataset_id = dataset_id_of(dataset)

    with http_client() as client:
        console.section(f"Storing UDP {UDP_ID}")
        put = client.put(f"/process_graphs/{UDP_ID}", json=udp_definition(dataset_id))
        put.raise_for_status()
        console.info(f"  {put.status_code} stored")

        listed = client.get("/process_graphs").json()
        ids = [graph.get("id") for graph in listed]
        console.info(f"  workflows now: {ids}")

    with climate_service() as service:
        console.section("Invoking the UDP via POST /result")
        graph = {
            "run": {"process_id": UDP_ID, "arguments": {"divisor": 1_000_000}, "result": True},
        }
        OUTPUT_DIR.mkdir(exist_ok=True)
        target = OUTPUT_DIR / f"{UDP_ID}.nc"
        try:
            result = service.execute(graph, path=target)
            console.info(f"  wrote {result}")
        except Exception as error:  # noqa: BLE001 - some UDPs need a save_result wrapper
            console.warn(f"  invocation returned: {error}")


if __name__ == "__main__":
    main()
