"""Deterministic compliance checker (Phase 3 stub)."""
from __future__ import annotations

import re
from typing import Any

from sembench.core.schema import BenchCase, ComplianceResult

# Basic PII patterns — expanded in Phase 3 with full rule YAML
_PII_PATTERNS: list[tuple[re.Pattern[str], str]] = [
    (re.compile(r"\d{6}-[1-4]\d{6}"), "resident_registration_number"),
    (re.compile(r"\d{4}[-\s]\d{4}[-\s]\d{4}[-\s]\d{4}"), "card_number"),
    (re.compile(r"[a-zA-Z0-9._%+\-]+@[a-zA-Z0-9.\-]+\.[a-zA-Z]{2,}"), "email_address"),
]


class ComplianceChecker:
    def check(self, case: BenchCase, redacted_payload: dict[str, Any]) -> ComplianceResult:
        import json
        payload_str = json.dumps(redacted_payload, ensure_ascii=False)
        pii_hits: list[str] = []
        violations: list[str] = []

        for pattern, reason in _PII_PATTERNS:
            matches = pattern.findall(payload_str)
            if matches:
                pii_hits.extend(matches)
                violations.append(f"{reason}: {matches[0]!r}")

        return ComplianceResult(
            case_id=case.id,
            passed=len(violations) == 0,
            violations=violations,
            pii_detected=pii_hits,
            risk_tier="high" if violations else "low",
        )
