# URL Monitor

[![CI](https://github.com/ongechiosiango/url-monitor/actions/workflows/ci.yml/badge.svg)](https://github.com/ongechiosiango/url-monitor/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Python 3.9+](https://img.shields.io/badge/python-3.9%2B-blue.svg)](https://www.python.org/downloads/)

Check a list of URLs concurrently and report status, latency, and HTTP code.

## Features

- Fires all checks concurrently via httpx + asyncio.
- Reports status (OK / REDIRECT / CLIENT ERR / SERVER ERR / ERROR), HTTP code, and latency.
- Reads URLs from positional args, a file, or stdin.
- Pretty rich terminal output, or `--json` for scripting.
- Non-zero exit code if any URL fails - easy to wire into cron or CI.

## Installation

From source:

    git clone git@github.com:ongechiosiango/url-monitor.git
    cd url-monitor
    python3 -m venv venv
    source venv/bin/activate
    pip install -e ".[dev]"

## Usage

    url-monitor https://example.com https://example.org

From a file:

    url-monitor --file urls.txt

From stdin:

    cat urls.txt | url-monitor --stdin

JSON output:

    url-monitor https://example.com --json

See docs/usage.md for full details.

## Development

    pip install -e ".[dev]"
    pytest -v

## Contributing

See CONTRIBUTING.md.

## License

MIT - see LICENSE.
