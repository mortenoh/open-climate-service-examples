"""Builders that assemble openEO process graphs from the typed models in :mod:`models`.

These return validated :class:`ProcessGraph` objects; call ``.to_payload()`` to get the
bare ``{node_id: {...}}`` mapping that :meth:`ClimateService.execute` accepts.
"""

from __future__ import annotations

from ocs_examples.models import (
    AggregateToChapArgs,
    AggregateToDhis2Args,
    ProcessGraph,
    ProcessNode,
    SaveFormat,
    SpatialExtent,
    TemporalExtent,
)


def aggregate_to_dhis2_graph(args: AggregateToDhis2Args) -> ProcessGraph:
    """Build a single-node graph that runs ``aggregate_to_dhis2_json``."""
    return ProcessGraph(
        nodes={
            "agg": ProcessNode(
                process_id="aggregate_to_dhis2_json",
                arguments=args.to_arguments(),
                result=True,
            )
        }
    )


def aggregate_to_chap_graph(args: AggregateToChapArgs) -> ProcessGraph:
    """Build a single-node graph that runs ``aggregate_to_chap_csv``."""
    return ProcessGraph(
        nodes={
            "agg": ProcessNode(
                process_id="aggregate_to_chap_csv",
                arguments=args.to_arguments(),
                result=True,
            )
        }
    )


def load_and_save_graph(
    dataset_id: str,
    temporal_extent: TemporalExtent,
    *,
    spatial_extent: SpatialExtent | None = None,
    bands: list[str] | None = None,
    save_format: SaveFormat = SaveFormat.NETCDF,
) -> ProcessGraph:
    """Build a ``load_collection`` -> ``save_result`` graph.

    The minimal "fetch this collection and hand it back in ``save_format``" pipeline,
    handy for downloading a subset without the openEO client.
    """
    load_arguments: dict[str, object] = {
        "id": dataset_id,
        "temporal_extent": temporal_extent.as_list(),
    }
    if spatial_extent is not None:
        load_arguments["spatial_extent"] = spatial_extent.model_dump()
    if bands is not None:
        load_arguments["bands"] = bands

    return ProcessGraph(
        nodes={
            "load": ProcessNode(process_id="load_collection", arguments=load_arguments),
            "save": ProcessNode(
                process_id="save_result",
                arguments={"data": {"from_node": "load"}, "format": save_format.value},
                result=True,
            ),
        }
    )
