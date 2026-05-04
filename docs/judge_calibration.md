# Judge Calibration

This benchmark uses SPS (Semantic Preservation Score), a 20-point rubric across five dimensions.

## Golden Set

The calibration target is 20 hand-scored Korean financial examples:

- 4 card transaction cases
- 4 insurance claim cases
- 4 debt optimization cases
- 3 banking cases
- 3 securities cases
- 2 tax cases

## Agreement Target

Phase 2 target: Cohen's kappa >= 0.7 between human baseline and Claude Opus judge scores after binning each dimension into low/medium/high.

The repository includes `sembench/judge/prompts/rubric_ko.md` as the Korean annotated prompt used for calibration.

## Bias Checks

Length bias:

- Compare a concise correct answer against a verbose answer with the same facts.
- Flag if the verbose answer consistently receives a higher score by more than 2/20.

Position bias:

- Swap reference/candidate order in the judge prompt during offline calibration.
- Flag if score deltas exceed 2/20.

## Current Status

The open-source CI path uses `MockProvider` for deterministic testing. Real Claude calibration should be run manually or in the validation workflow with `ANTHROPIC_API_KEY`.
