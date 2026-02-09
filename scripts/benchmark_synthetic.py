#!/usr/bin/env python3
"""Generate deterministic synthetic benchmark tables for public documentation."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

PROJECT = "Helm Suite"
METRICS = [{"scenario":"service health sweep","p50_ms":180,"p95_ms":320,"cpu_pct":15,"mem_mb":260},{"scenario":"security audit run","p50_ms":240,"p95_ms":410,"cpu_pct":19,"mem_mb":300},{"scenario":"config render check","p50_ms":95,"p95_ms":170,"cpu_pct":8,"mem_mb":140}]


def to_markdown(rows: list[dict]) -> str:
    lines = [
        f"# {PROJECT} Synthetic Benchmarks",
        "",
        "All metrics are synthetic and reproducible for documentation quality checks.",
        "",
        "| Scenario | p50 (ms) | p95 (ms) | CPU (%) | Memory (MB) |",
        "|---|---:|---:|---:|---:|",
    ]
    for row in rows:
        lines.append(
            f"| {row['scenario']} | {row['p50_ms']} | {row['p95_ms']} | {row['cpu_pct']} | {row['mem_mb']} |"
        )
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--format", choices=["markdown", "json"], default="markdown")
    parser.add_argument("--output", default="")
    args = parser.parse_args()

    if args.format == "json":
        content = json.dumps({"project": PROJECT, "synthetic": True, "metrics": METRICS}, indent=2) + "\n"
    else:
        content = to_markdown(METRICS)

    if args.output:
        Path(args.output).write_text(content)
    else:
        print(content, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
