"""Scan benchmark dataset files for direct identifier patterns."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sembench.compliance.checker import ComplianceChecker
from sembench.core.schema import BenchCase


def main() -> int:
    checker = ComplianceChecker()
    failures: list[str] = []
    for path in sorted(Path("datasets").rglob("*.json")):
        data = json.loads(path.read_text(encoding="utf-8"))
        for raw in data:
            case = BenchCase(**raw)
            result = checker.check(case, case.raw_context)
            high_risk = [v for v in result.violations if any(key in v for key in ["resident_registration_number", "foreign_registration_number", "credit_card_number", "account_number", "email", "phone_number", "policy_or_contract_number"])]
            if high_risk:
                failures.append(f"{path}:{case.id}: {high_risk[0]}")
    if failures:
        print("Dataset direct identifier scan failed:")
        print("\n".join(failures))
        return 1
    print("Dataset direct identifier scan passed.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
