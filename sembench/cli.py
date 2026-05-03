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


@app.command()
def run(
    config: Path = typer.Option(Path("configs/ci_smoke.yaml"), help="Run config YAML"),
    dataset: Path = typer.Option(Path("datasets/single_turn/card/L1_basic.json"), help="Dataset JSON"),
    out: Optional[Path] = typer.Option(None, help="Output JSON path"),
) -> None:
    """Run benchmark cases from a dataset file."""
    import yaml
    from sembench.adapters.builtins.passthrough import PassthroughAdapter
    from sembench.core.runner import BenchRunner
    from sembench.core.schema import BenchCase, RunConfig
    from sembench.llm.anthropic_provider import AnthropicProvider

    cfg_data = yaml.safe_load(config.read_text())
    run_cfg = RunConfig(**cfg_data)

    cases_raw = json.loads(dataset.read_text(encoding="utf-8"))
    cases = [BenchCase(**c) for c in cases_raw]

    adapter = PassthroughAdapter()
    provider = AnthropicProvider(model=run_cfg.judge_model)
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
