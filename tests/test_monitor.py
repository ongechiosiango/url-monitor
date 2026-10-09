"""Tests for the URL monitor."""

import asyncio
from pathlib import Path

import pytest

from url_monitor.monitor import CheckResult, check_urls, read_urls_from_file


def test_check_urls_empty_returns_empty():
    assert asyncio.run(check_urls([])) == []


def test_check_result_ok_true():
    r = CheckResult(url="x", status_code=200, latency_ms=10.0)
    assert r.ok is True


def test_check_result_ok_false_on_error():
    r = CheckResult(url="x", error="boom")
    assert r.ok is False


def test_check_result_ok_false_on_4xx():
    r = CheckResult(url="x", status_code=404, latency_ms=5.0)
    assert r.ok is False


def test_read_urls_skips_blanks_and_comments(tmp_path):
    p = tmp_path / "urls.txt"
    p.write_text(
        "# a comment\n"
        "\n"
        "https://example.com\n"
        "  https://example.org  \n"
        "\n"
        "# another comment\n"
        "https://example.net\n"
    )
    urls = read_urls_from_file(str(p))
    assert urls == ["https://example.com", "https://example.org", "https://example.net"]


@pytest.mark.parametrize("url", ["https://httpbin.org/status/200"])
def test_check_urls_basic(url):
    """Smoke test against a public endpoint (may be skipped in restricted networks)."""
    results = asyncio.run(check_urls([url], timeout=10.0))
    assert len(results) == 1
    assert results[0].url == url


def test_check_urls_invalid_host_records_error():
    results = asyncio.run(
        check_urls(["https://this-domain-does-not-exist-xyz.invalid"], timeout=5.0)
    )
    assert len(results) == 1
    assert results[0].ok is False
    assert results[0].error is not None
