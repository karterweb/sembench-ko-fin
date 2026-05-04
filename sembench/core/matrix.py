"""Dataset matrix loader for manifest-driven benchmark runs."""
from __future__ import annotations

import json
from collections import defaultdict
from pathlib import Path
from typing import Any

import yaml  # type: ignore[import-untyped]

from sembench.core.schema import BenchCase, Difficulty, Domain, RunConfig


class MatrixLoader:
    """Loads BenchCase objects from datasets/manifest.yaml and filters by run axes."""

    def __init__(self, manifest_path: Path = Path("datasets/manifest.yaml")) -> None:
        self.manifest_path = manifest_path
        self.dataset_root = manifest_path.parent

    def load(self, config: RunConfig) -> list[BenchCase]:
        manifest = yaml.safe_load(self.manifest_path.read_text(encoding="utf-8"))
        paths = self._collect_paths(manifest)
        cases: list[BenchCase] = []
        for rel_path in paths:
            file_path = self.dataset_root / rel_path
            if not file_path.exists():
                continue
            raw_cases = json.loads(file_path.read_text(encoding="utf-8"))
            cases.extend(BenchCase(**raw) for raw in raw_cases)

        filtered = [
            case
            for case in cases
            if self._domain_allowed(case.domain, config.domains)
            and self._difficulty_allowed(case.difficulty, config.difficulties)
        ]
        return self._sample_per_cell(filtered, config.sample_per_cell)

    def _collect_paths(self, node: Any) -> list[str]:
        paths: list[str] = []
        if isinstance(node, str) and node.endswith(".json"):
            return [node]
        if isinstance(node, list):
            for item in node:
                paths.extend(self._collect_paths(item))
        elif isinstance(node, dict):
            for key, value in node.items():
                if key in {"version", "ci_smoke"}:
                    continue
                paths.extend(self._collect_paths(value))
        return paths

    def _sample_per_cell(self, cases: list[BenchCase], sample_per_cell: int) -> list[BenchCase]:
        if sample_per_cell <= 0:
            return cases
        cells: dict[tuple[Domain, Difficulty], list[BenchCase]] = defaultdict(list)
        for case in sorted(cases, key=lambda c: c.id):
            cells[(case.domain, case.difficulty)].append(case)
        sampled: list[BenchCase] = []
        for cell_cases in cells.values():
            sampled.extend(cell_cases[:sample_per_cell])
        return sorted(sampled, key=lambda c: c.id)

    def _domain_allowed(self, domain: Domain, allowed: list[Domain]) -> bool:
        return not allowed or domain in allowed

    def _difficulty_allowed(self, difficulty: Difficulty, allowed: list[Difficulty]) -> bool:
        return not allowed or difficulty in allowed
