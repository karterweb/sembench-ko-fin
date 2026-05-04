"""CLI entry point for sembench."""
from __future__ import annotations

import json
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console
from rich.table import Table

app = typer.Typer(help="sembench-ko-fin: semantic pseudonymization benchmark")
console = Console()
report_app = typer.Typer(help="Reporting commands")
app.add_typer(report_app, name="report")


@app.command()
def run(
    config: Path = typer.Option(Path("configs/ci_smoke.yaml"), help="Run config YAML"),
    dataset: Optional[Path] = typer.Option(None, help="Dataset JSON. If omitted, manifest matrix is used."),
    out: Optional[Path] = typer.Option(None, help="Output JSON path"),
) -> None:
    """Run benchmark cases from a dataset file."""
    import yaml  # type: ignore[import-untyped]
    from sembench.adapters.builtins.passthrough import PassthroughAdapter
    from sembench.adapters.builtins.semantic_redaction_ko import SemanticRedactionKoAdapter
    from sembench.core.matrix import MatrixLoader
    from sembench.core.runner import BenchRunner
    from sembench.core.schema import BenchCase, RunConfig
    from sembench.llm.anthropic_provider import AnthropicProvider
    from sembench.llm.mock_provider import MockProvider

    cfg_data = yaml.safe_load(config.read_text())
    run_cfg = RunConfig(**cfg_data)

    if dataset:
        cases_raw = json.loads(dataset.read_text(encoding="utf-8"))
        cases = [BenchCase(**c) for c in cases_raw]
    else:
        cases = MatrixLoader().load(run_cfg)

    adapter = (
        SemanticRedactionKoAdapter()
        if run_cfg.adapter_id == "semantic-redaction-ko"
        else PassthroughAdapter()
    )
    provider = (
        MockProvider(model=run_cfg.judge_model)
        if run_cfg.judge_model.startswith("mock")
        else AnthropicProvider(model=run_cfg.judge_model)
    )
    runner = BenchRunner(adapter=adapter, provider=provider, config=run_cfg)

    console.print(f"[bold]Running {len(cases)} cases[/bold] with adapter=[cyan]{adapter.adapter_id}[/cyan]")
    bench = runner.run(cases)

    table = Table(title="Results")
    table.add_column("Case ID")
    table.add_column("SPS")
    table.add_column("Compliance")
    for r in bench.results:
        table.add_row(r.case_id, f"{r.sps.normalized:.2f}", "✓" if r.compliance.passed else "✗")
    console.print(table)
    console.print(f"Mean SPS: [bold]{bench.mean_sps:.3f}[/bold]  Cost: ${bench.total_cost_usd:.4f}")

    if out:
        out.write_text(json.dumps(bench.model_dump(mode="json"), ensure_ascii=False, indent=2))
        console.print(f"Saved to [green]{out}[/green]")


if __name__ == "__main__":
    app()


@report_app.command("html")
def report_html(
    input: Path = typer.Option(..., help="BenchRun JSON path"),
    out: Path = typer.Option(Path("results/report.html"), help="HTML report path"),
) -> None:
    """Render an HTML report from a BenchRun JSON file."""
    from sembench.reporting.html_report import render_html_report

    render_html_report(input, out)
    console.print(f"Saved HTML report to [green]{out}[/green]")


@report_app.command("leaderboard")
def report_leaderboard(
    inputs: list[Path] = typer.Argument(..., help="BenchRun JSON files"),
) -> None:
    """Rank multiple run outputs by SPS, compliance, and cost efficiency."""
    from sembench.reporting.leaderboard import build_leaderboard

    rows = build_leaderboard(inputs)
    table = Table(title="Leaderboard")
    table.add_column("Run")
    table.add_column("Adapter")
    table.add_column("Mean SPS")
    table.add_column("Compliance")
    table.add_column("Cost efficiency")
    for row in rows:
        table.add_row(
            str(row["run_id"]),
            str(row["adapter_id"]),
            f"{float(row['mean_sps']):.3f}",
            f"{float(row['compliance_rate']):.1%}",
            f"{float(row['cost_efficiency']):.1f}",
        )
    console.print(table)
