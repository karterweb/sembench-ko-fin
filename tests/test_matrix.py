"""Tests for manifest-driven matrix loading."""
from __future__ import annotations

from collections import Counter

from sembench.core.matrix import MatrixLoader
from sembench.core.schema import Difficulty, Domain, RunConfig


def test_matrix_loader_loads_all_domains() -> None:
    cases = MatrixLoader().load(RunConfig(run_id="all", adapter_id="x", sample_per_cell=0))
    domains = {case.domain for case in cases}
    assert {domain for domain in Domain}.issubset(domains)
    assert len(cases) >= 150


def test_matrix_loader_filters_and_samples_per_cell() -> None:
    cfg = RunConfig(
        run_id="sample",
        adapter_id="x",
        domains=[Domain.CARD],
        difficulties=[Difficulty.L1, Difficulty.L2],
        sample_per_cell=1,
    )
    cases = MatrixLoader().load(cfg)
    assert len(cases) == 2
    assert {case.domain for case in cases} == {Domain.CARD}
    assert Counter(case.difficulty for case in cases) == {Difficulty.L1: 1, Difficulty.L2: 1}
