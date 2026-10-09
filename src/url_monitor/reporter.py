"""Rich terminal reporter for URL check results."""

from __future__ import annotations

import json

from rich.console import Console
from rich.table import Table

from .monitor import CheckResult

console = Console()


def _status_label(r: CheckResult) -> str:
    if r.error:
        return "[red]ERROR[/red]"
    if r.status_code is None:
        return "[red]NO RESPONSE[/red]"
    if 200 <= r.status_code < 300:
        return "[green]OK[/green]"
    if 300 <= r.status_code < 400:
        return "[cyan]REDIRECT[/cyan]"
    if 400 <= r.status_code < 500:
        return "[yellow]CLIENT ERR[/yellow]"
    return "[red]SERVER ERR[/red]"


def print_report(results, total_time_s: float) -> None:
    """Print the results as a table."""
    console.print()
    console.rule("[bold cyan]URL Monitor[/bold cyan]")

    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("URL", style="cyan", no_wrap=False, overflow="fold")
    table.add_column("Status", no_wrap=True)
    table.add_column("Code", justify="right", style="green")
    table.add_column("Latency (ms)", justify="right", style="green")
    table.add_column("Error", style="red", overflow="fold")

    for r in results:
        table.add_row(
            r.url,
            _status_label(r),
            str(r.status_code) if r.status_code is not None else "-",
            f"{r.latency_ms:.1f}",
            r.error or "",
        )

    console.print(table)

    total = len(results)
    ok = sum(1 for r in results if r.ok)
    console.print(
        f"\n[bold]Checked {total} URL(s)[/bold]: "
        f"[green]{ok} OK[/green], "
        f"[red]{total - ok} failing[/red] "
        f"in {total_time_s:.2f}s"
    )


def to_json(results, total_time_s: float) -> str:
    """Serialize results as JSON."""
    return json.dumps(
        {
            "total": len(results),
            "ok": sum(1 for r in results if r.ok),
            "total_time_s": round(total_time_s, 3),
            "results": [
                {
                    "url": r.url,
                    "ok": r.ok,
                    "status_code": r.status_code,
                    "latency_ms": round(r.latency_ms, 2),
                    "error": r.error,
                }
                for r in results
            ],
        },
        indent=2,
    )
