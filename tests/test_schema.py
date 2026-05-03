"""Smoke tests for core schema and compliance checker."""
from __future__ import annotations

import json
from pathlib import Path

import pytest

from sembench.compliance.checker import ComplianceChecker
from sembench.core.schema import BenchCase, Domain, Difficulty, TurnType


CARD_L1_PATH = Path(__file__).parent.parent / "datasets/single_turn/card/L1_basic.json"


def _load_cases() -> list[BenchCase]:
    data = json.loads(CARD_L1_PATH.read_text(encoding="utf-8"))
    return [BenchCase(**c) for c in data]


def test_card_l1_loads() -> None:
    cases = _load_cases()
    assert len(cases) >= 3


def test_card_l1_fields() -> None:
    cases = _load_cases()
    case = cases[0]
    assert case.id == "card-L1-001"
    assert case.domain == Domain.CARD
    assert case.difficulty == Difficulty.L1
    assert case.turn_type == TurnType.SINGLE
    assert case.raw_utterance
    assert case.reference_answer


def test_compliance_checker_passes_clean_payload() -> None:
    cases = _load_cases()
    checker = ComplianceChecker()
    clean_payload = {
        "merchant_taxonomy": "coffee_chain",
        "amount_relation": "same_amount",
        "temporal_relation": "near_time_duplicate",
        "authorization_lifecycle": ["approved", "cancelled"],
    }
    result = checker.check(cases[0], clean_payload)
    assert result.passed
    assert result.violations == []


def test_compliance_checker_detects_card_number() -> None:
    cases = _load_cases()
    checker = ComplianceChecker()
    leaky_payload = {"card": "1234-5678-9012-3456", "merchant": "starbucks"}
    result = checker.check(cases[0], leaky_payload)
    assert not result.passed
    assert result.risk_tier == "high"
