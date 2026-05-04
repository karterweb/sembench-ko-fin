"""Deterministic compliance checker for Korean financial pseudonymization."""
from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Literal, cast

import yaml  # type: ignore[import-untyped]

from sembench.core.schema import BenchCase, ComplianceResult

RULE_DIR = Path(__file__).parent / "rules"
RISK_ORDER = {"low": 0, "medium": 1, "high": 2}


class CompiledRule:
    def __init__(self, rule_id: str, regex: str, severity: str) -> None:
        self.rule_id = rule_id
        self.regex = re.compile(regex)
        self.severity = cast(Literal["low", "medium", "high"], severity if severity in RISK_ORDER else "low")


def _load_rules() -> list[CompiledRule]:
    data = yaml.safe_load((RULE_DIR / "pii_patterns.yaml").read_text(encoding="utf-8"))
    return [
        CompiledRule(
            rule_id=str(item["id"]),
            regex=str(item["regex"]),
            severity=str(item["severity"]),
        )
        for item in data["patterns"]
    ]


_PII_RULES = _load_rules()


class ComplianceChecker:
    def check(self, case: BenchCase, redacted_payload: dict[str, Any]) -> ComplianceResult:
        import json
        payload_str = json.dumps(redacted_payload, ensure_ascii=False)
        pii_hits: list[str] = []
        violations: list[str] = []
        highest_risk: Literal["low", "medium", "high"] = "low"

        for rule in _PII_RULES:
            matches = rule.regex.findall(payload_str)
            if matches:
                normalized_matches = [m if isinstance(m, str) else "".join(m) for m in matches]
                pii_hits.extend(normalized_matches)
                violations.append(f"{rule.rule_id}: {normalized_matches[0]!r}")
                if RISK_ORDER[rule.severity] > RISK_ORDER[highest_risk]:
                    highest_risk = rule.severity

        return ComplianceResult(
            case_id=case.id,
            passed=len(violations) == 0,
            violations=violations,
            pii_detected=pii_hits,
            risk_tier=highest_risk,
        )
