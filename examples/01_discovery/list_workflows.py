"""List the stored workflows (user-defined processes) on an instance.

``service.workflows()`` returns the saved process graphs (``GET /process_graphs``) —
reusable, parameterised pipelines such as ``aggregate_to_dhis2_json`` and
``aggregate_to_chap_csv``. These are what you invoke from the DHIS2 examples.

Run:
    uv run python examples/01_discovery/list_workflows.py
"""

from __future__ import annotations

from ocs_examples import climate_service, console


def main() -> None:
    """Print every stored workflow id and its summary."""
    with climate_service() as service:
        workflows = service.workflows()

    console.section(f"Stored workflows ({len(workflows)})")
    if not workflows:
        console.warn("No stored workflows. See examples/03_openeo/store_and_run_udp.py to add one.")
        return

    for workflow in workflows:
        summary = workflow.get("summary") or workflow.get("description") or ""
        print(f"  {workflow.get('id', '?'):<32} {summary}")


if __name__ == "__main__":
    main()
