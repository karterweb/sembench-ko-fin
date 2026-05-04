"""Leaderboard utilities for comparing BenchRun JSON files."""
from __future__ import annotations

import json
from pathlib import Path

from sembench.core.schema import BenchRun


def build_leaderboard(paths: list[Path]) -> list[dict[str, float | str]]:
    rows: list[dict[str, float | str]] = []
    for path in paths:
        run = BenchRun(**json.loads(path.read_text(encoding="utf-8")))
        total = len(run.results) or 1
        compliance_rate = run.passed_compliance / total
        cost_efficiency = run.mean_sps / max(run.total_cost_usd, 0.0001)
        rows.append(
            {
                "run_id": run.config.run_id,
                "adapter_id": run.config.adapter_id,
                "mean_sps": run.mean_sps,
                "compliance_rate": compliance_rate,
                "cost_efficiency": cost_efficiency,
            }
        )
    return sorted(rows, key=lambda row: (-float(row["mean_sps"]), -float(row["compliance_rate"])))
