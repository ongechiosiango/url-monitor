"""Command-line interface for URL Monitor."""

from __future__ import annotations

import argparse
import asyncio
import sys
import time
from pathlib import Path

from rich.console import Console

from . import __version__
from .monitor import check_urls, read_urls_from_file
from .reporter import print_report, to_json

console = Console()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="url-monitor",
        description="Check a list of URLs concurrently and report status, latency, and HTTP code.",
    )
    parser.add_argument("urls", nargs="*", help="One or more URLs to check.")
    parser.add_argument("--file", "-f", help="Read URLs from a file (one per line).")
    parser.add_argument("--stdin", action="store_true", help="Read URLs from stdin.")
    parser.add_argument("--timeout", "-t", type=float, default=10.0,
                        help="Per-URL timeout in seconds (default: 10).")
    parser.add_argument("--method", "-m", default="GET",
                        help="HTTP method to use (default: GET).")
    parser.add_argument("--concurrency", "-c", type=int, default=10,
                        help="Max concurrent checks (default: 10).")
    parser.add_argument("--json", action="store_true", dest="as_json",
                        help="Output results as JSON.")
    parser.add_argument("--version", action="version", version=f"url-monitor {__version__}")
    return parser


def _collect_urls(args) -> list:
    urls = list(args.urls)
    if args.file:
        p = Path(args.file)
        if not p.exists():
            raise FileNotFoundError(f"URL list file not found: {args.file}")
        urls.extend(read_urls_from_file(str(p)))
    if args.stdin:
        for raw in sys.stdin:
            line = raw.strip()
            if line and not line.startswith("#"):
                urls.append(line)
    # Deduplicate preserving order
    seen = set()
    unique = []
    for u in urls:
        if u not in seen:
            seen.add(u)
            unique.append(u)
    return unique


def main() -> int:
    args = build_parser().parse_args()

    try:
        urls = _collect_urls(args)
    except FileNotFoundError as exc:
        console.print(f"[bold red]Error:[/bold red] {exc}")
        return 1

    if not urls:
        console.print("[bold yellow]No URLs provided.[/bold yellow] Use positional args, --file, or --stdin.")
        return 1

    start = time.perf_counter()
    try:
        results = asyncio.run(
            check_urls(
                urls,
                timeout=args.timeout,
                method=args.method.upper(),
                concurrency=args.concurrency,
            )
        )
    except KeyboardInterrupt:
        print("\nAborted by user.", file=sys.stderr)
        return 130
    total_time = time.perf_counter() - start

    if args.as_json:
        print(to_json(results, total_time))
    else:
        print_report(results, total_time)

    return 0 if all(r.ok for r in results) else 2


if __name__ == "__main__":
    raise SystemExit(main())
