"""Core: fire concurrent HEAD (or GET) requests and report results."""

from __future__ import annotations

import asyncio
import time
from dataclasses import dataclass
from typing import List, Optional

import httpx


@dataclass
class CheckResult:
    """The result of checking one URL."""

    url: str
    status_code: Optional[int] = None
    latency_ms: float = 0.0
    error: Optional[str] = None

    @property
    def ok(self) -> bool:
        return self.error is None and self.status_code is not None and 200 <= self.status_code < 400


async def _check_one(
    client: httpx.AsyncClient,
    url: str,
    method: str,
) -> CheckResult:
    start = time.perf_counter()
    try:
        response = await client.request(method, url)
        elapsed_ms = (time.perf_counter() - start) * 1000
        return CheckResult(url=url, status_code=response.status_code, latency_ms=elapsed_ms)
    except Exception as exc:  # noqa: BLE001
        elapsed_ms = (time.perf_counter() - start) * 1000
        return CheckResult(url=url, latency_ms=elapsed_ms, error=str(exc))


async def check_urls(
    urls: List[str],
    timeout: float = 10.0,
    method: str = "GET",
    concurrency: int = 10,
    follow_redirects: bool = True,
) -> List[CheckResult]:
    """Check all URLs concurrently and return the results in order."""
    if not urls:
        return []

    semaphore = asyncio.Semaphore(max(1, concurrency))
    limits = httpx.Limits(max_connections=concurrency, max_keepalive_connections=concurrency)

    async def _guarded(url: str) -> CheckResult:
        async with semaphore:
            return await _check_one(client, url, method)

    async with httpx.AsyncClient(
        timeout=timeout,
        limits=limits,
        follow_redirects=follow_redirects,
        headers={"User-Agent": "url-monitor/0.1.0"},
    ) as client:
        return list(await asyncio.gather(*(_guarded(u) for u in urls)))


def read_urls_from_file(path: str) -> List[str]:
    """Read URLs from a text file, one per line. Skips blanks and # comments."""
    urls = []
    with open(path, "r", encoding="utf-8") as fh:
        for raw in fh:
            line = raw.strip()
            if not line or line.startswith("#"):
                continue
            urls.append(line)
    return urls
