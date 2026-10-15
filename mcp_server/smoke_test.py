"""
Smoke test for the MCP server: calls every tool once and reports pass/fail.

Run from the project root:
    venv\\Scripts\\python.exe -m mcp_server.smoke_test

Prediction tools work without a database. The read-only data tools need
PostgreSQL up; if it is down they are reported as SKIP, not FAIL.
"""
from __future__ import annotations

import asyncio
import json

from django.db import OperationalError

from mcp_server import server

# (tool callable, kwargs, needs_database)
CHECKS = [
    (server.list_symptoms, {}, False),
    (server.list_diseases, {}, False),
    (server.model_info, {}, False),
    (server.predict_disease, {
        'symptoms': ['fever', 'udder_swelling', 'milk_clots', 'udder_pain'],
        'breed': 'Brahman',
        'province': 'Midlands',
    }, False),
    (server.system_stats, {}, True),
    (server.list_cases, {'limit': 3}, True),
    (server.list_farmers, {'limit': 3}, True),
    (server.list_vets, {'limit': 3}, True),
    (server.disease_stats_by_province, {}, True),
]


def _unwrap(tool):
    """mcp 2.x @app.tool() returns the original function; 1.x wrapped it."""
    return getattr(tool, 'fn', tool)


def main() -> int:
    failures = 0
    skipped = 0

    for tool, kwargs, needs_db in CHECKS:
        fn = _unwrap(tool)
        name = getattr(fn, '__name__', str(tool))
        try:
            result = fn(**kwargs)
            if asyncio.iscoroutine(result):
                result = asyncio.run(result)

            if isinstance(result, dict) and 'error' in result:
                print(f"FAIL  {name}: {result['error']}")
                failures += 1
                continue

            preview = json.dumps(result, default=str)
            if len(preview) > 160:
                preview = preview[:157] + '...'
            print(f"PASS  {name}: {preview}")

        except OperationalError as exc:
            if needs_db:
                print(f"SKIP  {name}: database unreachable ({str(exc).strip()[:60]})")
                skipped += 1
            else:
                print(f"FAIL  {name}: unexpected database error: {exc}")
                failures += 1
        except Exception as exc:  # noqa: BLE001 - smoke test reports everything
            print(f"FAIL  {name}: {type(exc).__name__}: {exc}")
            failures += 1

    total = len(CHECKS)
    print(f"\n{total - failures - skipped}/{total} passed, {skipped} skipped, {failures} failed")

    # Confirm the tools are actually registered with the MCP app.
    tools = asyncio.run(server.app.list_tools())
    print(f"Registered MCP tools ({len(tools)}): {', '.join(t.name for t in tools)}")

    return 1 if failures else 0


if __name__ == '__main__':
    raise SystemExit(main())
