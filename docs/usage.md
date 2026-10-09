# Usage Guide

## Check inline URLs

    url-monitor https://example.com https://example.org

## Check URLs from a file

    url-monitor --file urls.txt

The file should have one URL per line. Blank lines and lines starting with
`#` are ignored.

## Check URLs from stdin

    cat urls.txt | url-monitor --stdin

## JSON output

    url-monitor https://example.com --json

## Options

| Flag | Short | Default | Description |
|------|-------|---------|-------------|
| --file | -f | (none) | Read URLs from a file |
| --stdin | | off | Read URLs from stdin |
| --timeout | -t | 10.0 | Per-URL timeout in seconds |
| --method | -m | GET | HTTP method |
| --concurrency | -c | 10 | Max concurrent checks |
| --json | | off | Output as JSON |

## Exit codes

- 0 - all URLs returned 2xx or 3xx
- 1 - no URLs provided, or the input file was missing
- 2 - one or more URLs failed
