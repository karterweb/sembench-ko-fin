"""End-to-end smoke test using MockProvider and PassthroughAdapter."""
from __future__ import annotations

import json
from pathlib import Path

from sembench.adapters.builtins.passthrough import PassthroughAdapter
from sembench.core.runner import BenchRunner
from sembench.core.schema import BenchCase, RunConfig
from sembench.llm.mock_provider import MockProvider

CARD_L1_PATH = Path(__file__).parent.parent / "datasets/single_turn/card/L1_basic.json"


def _load_cases() -> list[BenchCase]:
    data = json.loads(CARD_L1_PATH.read_text(encoding="utf-8"))
    return [BenchCase(**c) for c in data]


def test_e2e_full_run() -> None:
    """BenchRunner completes all cases with MockProvider + PassthroughAdapter."""
    cases = _load_cases()
    provider = MockProvider()
    adapter = PassthroughAdapter()
    config = RunConfig(run_id="smoke-001", adapter_id=adapter.adapter_id)

    runner = BenchRunner(adapter=adapter, provider=provider, config=config)
    bench = runner.run(cases)

    assert bench.aborted is False
    assert len(bench.results) == len(cases)
    assert bench.mean_sps > 0.0


def test_e2e_cost_guard_abort() -> None:
    """BenchRunner aborts immediately when max_cost_usd=0.0."""
    cases = _load_cases()
    provider = MockProvider()
    adapter = PassthroughAdapter()
    config = RunConfig(
        run_id="smoke-abort",
        adapter_id=adapter.adapter_id,
        max_cost_usd=0.0,
    )

    runner = BenchRunner(adapter=adapter, provider=provider, config=config)
    bench = runner.run(cases)

    assert bench.aborted is True
