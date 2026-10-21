# Gold Data Pipeline

Downloads historical gold prices, validates them, and writes a clean OHLC CSV for the
prediction models. It is a standalone batch job, separate from the FastAPI backend: it starts,
downloads, validates, writes a file, and exits.

## Data source

Prices come from Yahoo Finance through [`yfinance`](https://github.com/ranaroussi/yfinance),
an unofficial scraper with no availability guarantees.

| Ticker | What it is | Status |
|---|---|---|
| `XAUUSD=X` | Gold spot price | Currently returns `404 Quote not found` from Yahoo, so it is not usable as the default. |
| `GC=F` | COMEX gold **futures** (continuous contract) | Works. This is the working source. |

> **Phase 1 uses futures as a proxy for spot gold.** `GC=F` tracks spot closely but is a futures
> series: it can show offsets and discontinuities around contract rolls, and large moves can differ
> from spot (for example, the 2026-01-30 crash was larger in futures than in spot). Every row stores
> its source in a `ticker` column so futures and spot data are never mixed unknowingly.

The default ticker in the CLI is still `XAUUSD=X`, so always pass `--ticker GC=F` for now.

## Requirements

- Python 3.11 or newer
- Docker (optional, for containerized runs)

## Setup

Create a virtual environment **inside this folder**, so it stays isolated from the backend's:

```powershell
cd backend\data_pipeline
python -m venv .venv
.\.venv\Scripts\Activate.ps1
pip install -e ".[dev]"
```

On macOS or Linux, activate with `source .venv/bin/activate`.

## Usage

```powershell
python -m gold_pipeline.ingestion --ticker GC=F --start 2020-01-01 --end 2026-10-01 --output data/raw/gc_f.csv
```

| Option | Default | Description |
|---|---|---|
| `--ticker` | `XAUUSD=X` | Yahoo ticker symbol. |
| `--start` | `2020-01-01` | First date, inclusive. |
| `--end` | none | Last date, **exclusive**. Set it for reproducible files; without it the latest row may be incomplete. |
| `--output` | `data/raw/xauusd.csv` | Output CSV path, relative to the current directory. Name it after the ticker, for example `gc_f.csv`. |

Generated data is git-ignored and never committed.

### Output schema

| Column | Description |
|---|---|
| `date` | Timezone-naive calendar date, sorted ascending, unique. |
| `open`, `high`, `low`, `close` | Prices. Validated numeric, finite, and positive. |
| `adj_close`, `volume` | Passed through from Yahoo, not validated. |
| `ticker` | Source ticker for the row. |

## Validation

`validate_ohlc` rejects the whole dataset if any of these fail. The error reports the number of bad
rows and the first few dates.

- empty data, missing required columns, duplicate column names
- unparseable or missing dates, duplicate timestamps
- missing, nonnumeric, infinite, zero, or negative prices
- `high` below `open`, `low`, or `close`; `low` above `open`, `high`, or `close`

Two helpers **report without failing**, because real markets contain large moves and holiday gaps:

- `find_suspicious_moves`: close-to-close moves above a threshold (default 8%, a placeholder to be
  tuned on real data)
- `find_large_gaps`: calendar gaps longer than a limit (default 5 days)

Ingestion logs both as warnings. Do not drop flagged rows without checking them: the 2026-01-30
flag in the current data is a real market event, not a data error.

## Docker

```powershell
docker build -t xauusd-data-pipeline .

docker run --rm `
  -v "${PWD}/data:/app/data" `
  xauusd-data-pipeline `
  --ticker GC=F --start 2020-01-01 --end 2026-10-01 --output data/raw/gc_f.csv
```

The container's working directory is `/app`, so a relative `--output` under `data/` lands in the
mounted host folder. The package is installed into the image at build time, so **rebuild after every
code change**; otherwise the container runs the old code.

## Development

```powershell
ruff check .
ruff format --check .
pytest
```

Run these from this folder with its virtual environment active. `pyproject.toml` here configures
pytest and ruff, so running them from the repository root fails with import errors.

## CI

`.github/workflows/python-ci.yml` runs on pushes to `main` and on pull requests that touch this
folder:

1. Lint, format check, and tests on Python 3.11 and 3.13
2. Docker image build and an import smoke test

CI makes no network calls to Yahoo, so a provider outage cannot break it.

## Project layout

```
data_pipeline/
├── src/gold_pipeline/
│   ├── ingestion.py      # download, retry, normalize, write CSV
│   └── validation.py     # OHLC validation and reporting helpers
├── tests/
│   └── test_validation.py
├── data/                 # generated, git-ignored
├── Dockerfile
├── pyproject.toml
└── README.md
```

## Known limitations

- Single unofficial data source. The download function is isolated in `_fetch_yahoo` so another
  provider can be added without touching validation.
- Daily bars only; the timezone handling assumes daily data.
- The ingestion download path is not yet covered by tests (the Yahoo call needs mocking).