# Architecture

```text
BenchCase dataset
  -> MatrixLoader
  -> PseudonymizationAdapter
  -> External LLM Provider
  -> SPS Judge
  -> ComplianceChecker
  -> BenchRun JSON
  -> HTML report / leaderboard
```

## Responsibilities

- `sembench.core.schema`: Pydantic contracts for cases, configs, scores, and run output.
- `sembench.core.matrix`: manifest-driven dataset loading and sampling by domain/difficulty cell.
- `sembench.adapters`: pluggable pseudonymization systems under test.
- `sembench.compliance`: deterministic rule engine for Korean financial PII and sensitive leakage.
- `sembench.judge`: LLM-as-judge SPS rubric.
- `sembench.reporting`: HTML reports and leaderboard comparison.

## Risk Model

L1/L2 cases measure ordinary utility preservation. L3/L4 cases stress cross-reference attacks, purpose limitation, additional-information separation, and Innovative Financial Services edge conditions.
