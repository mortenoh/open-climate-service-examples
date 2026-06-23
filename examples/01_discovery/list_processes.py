"""List the openEO processes an instance offers.

``service.processes()`` returns the standard openEO process catalog (``GET /processes``)
— the building blocks (``load_collection``, ``apply``, ``reduce_dimension``,
``save_result``, ...) you compose into process graphs.

Run:
    uv run python examples/01_discovery/list_processes.py
"""

from __future__ import annotations

from ocs_examples import climate_service, console


def main() -> None:
    """Print every process id and its one-line summary."""
    with climate_service() as service:
        processes = service.processes()

    console.section(f"Available processes ({len(processes)})")
    for process in sorted(processes, key=lambda p: str(p.get("id", ""))):
        summary = process.get("summary") or process.get("description") or ""
        summary = summary.splitlines()[0] if summary else ""
        print(f"  {process['id']:<28} {summary[:80]}")


if __name__ == "__main__":
    main()
