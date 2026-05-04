"""Compliance checker pattern coverage."""
from __future__ import annotations

from sembench.compliance.checker import ComplianceChecker
from sembench.core.schema import BenchCase


def _case() -> BenchCase:
    return BenchCase(
        id="compliance-fixture",
        domain="card",
        service="chatbot",
        turn_type="single",
        difficulty="L1",
        strategy="taxonomy",
        raw_utterance="fixture",
        raw_context={},
        reference_answer="fixture",
    )


def test_compliance_patterns_detect_11_types() -> None:
    samples = {
        "rrn": "900101-1234567",
        "foreign": "900101-5234567",
        "card": "1234-5678-9012-3456",
        "business": "123-45-67890",
        "account": "110-123-456789",
        "email": "user@example.com",
        "phone": "010-1234-5678",
        "institution": "신한은행",
        "hospital": "서울아산병원",
        "amount": "1,234,000원",
        "policy": "LIFE-2020-889172",
    }
    checker = ComplianceChecker()
    for value in samples.values():
        result = checker.check(_case(), {"leak": value})
        assert not result.passed, value
        assert result.violations


def test_taxonomy_tokens_pass() -> None:
    result = ComplianceChecker().check(
        _case(),
        {
            "merchant_taxonomy": "coffee_chain",
            "relation": "near_time_duplicate_within_2_minutes",
            "amount": "medium_amount_band",
        },
    )
    assert result.passed
