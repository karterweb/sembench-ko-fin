"""HTML reporting for BenchRun JSON outputs."""
from __future__ import annotations

import html
import json
from pathlib import Path

from sembench.core.schema import BenchRun


def _render_template(run: BenchRun) -> str:
    rows = "\n".join(
        f"""      <tr>
        <td>{html.escape(result.case_id)}</td>
        <td>{result.sps.normalized:.3f}</td>
        <td class="{'pass' if result.compliance.passed else 'fail'}">{'PASS' if result.compliance.passed else 'FAIL'}</td>
        <td>{html.escape(result.compliance.risk_tier)}</td>
        <td>{html.escape(', '.join(result.compliance.violations))}</td>
      </tr>"""
        for result in run.results
    )
    return f"""<!doctype html>
<html lang="ko">
<head>
  <meta charset="utf-8">
  <title>sembench-ko-fin report</title>
  <style>
    body {{ font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", sans-serif; margin: 32px; }}
    table {{ border-collapse: collapse; width: 100%; margin-top: 16px; }}
    th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
    th {{ background: #f5f5f5; }}
    .pass {{ color: #137333; font-weight: 700; }}
    .fail {{ color: #b3261e; font-weight: 700; }}
  </style>
</head>
<body>
  <h1>sembench-ko-fin report</h1>
  <p><strong>Run:</strong> {html.escape(run.config.run_id)} | <strong>Adapter:</strong> {html.escape(run.config.adapter_id)}</p>
  <p><strong>Mean SPS:</strong> {run.mean_sps:.3f} | <strong>Compliance:</strong> {run.passed_compliance}/{len(run.results)}</p>
  <table>
    <thead><tr><th>Case</th><th>SPS</th><th>Compliance</th><th>Risk</th><th>Violations</th></tr></thead>
    <tbody>
{rows}
    </tbody>
  </table>
</body>
</html>"""


def render_html_report(input_path: Path, out_path: Path) -> None:
    run = BenchRun(**json.loads(input_path.read_text(encoding="utf-8")))
    out_path.parent.mkdir(parents=True, exist_ok=True)
    out_path.write_text(_render_template(run), encoding="utf-8")
