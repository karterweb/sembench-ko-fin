"""Tests for reference adapter and reporting utilities."""
from __future__ import annotations

import json
from pathlib import Path

from sembench.adapters.builtins.passthrough import PassthroughAdapter
from sembench.adapters.builtins.semantic_redaction_ko import SemanticRedactionKoAdapter
from sembench.compliance.checker import ComplianceChecker
from sembench.core.matrix import MatrixLoader
from sembench.core.runner import BenchRunner
from sembench.core.schema import RunConfig
from sembench.llm.mock_provider import MockProvider
from sembench.reporting.html_report import render_html_report
from sembench.reporting.leaderboard import build_leaderboard


def test_semantic_redaction_adapter_suppresses_sensitive_context() -> None:
    case = next(c for c in MatrixLoader().load(RunConfig(run_id="all", adapter_id="x", sample_per_cell=0)) if c.id == "card-L1-001")
    payload = SemanticRedactionKoAdapter().redact(case.raw_utterance, case.raw_context)
    assert ComplianceChecker().check(case, payload).passed
    assert "techniques_applied" in payload


def test_adversarial_passthrough_fails_compliance() -> None:
    case = next(c for c in MatrixLoader().load(RunConfig(run_id="all", adapter_id="x", sample_per_cell=0)) if c.id == "card-L3-003")
    payload = PassthroughAdapter().redact(case.raw_utterance, case.raw_context)
    assert not ComplianceChecker().check(case, payload).passed


def test_html_report_and_leaderboard(tmp_path: Path) -> None:
    cases = MatrixLoader().load(
        RunConfig(run_id="report-test", adapter_id="semantic-redaction-ko", sample_per_cell=1, domains=["card"], difficulties=["L1"])
    )
    runner = BenchRunner(
        adapter=SemanticRedactionKoAdapter(),
        provider=MockProvider(),
        config=RunConfig(run_id="report-test", adapter_id="semantic-redaction-ko"),
    )
    bench = runner.run(cases)
    run_path = tmp_path / "run.json"
    html_path = tmp_path / "report.html"
    run_path.write_text(json.dumps(bench.model_dump(mode="json"), ensure_ascii=False), encoding="utf-8")
    render_html_report(run_path, html_path)
    assert "sembench-ko-fin report" in html_path.read_text(encoding="utf-8")
    assert build_leaderboard([run_path])[0]["adapter_id"] == "semantic-redaction-ko"
