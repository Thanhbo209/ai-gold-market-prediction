"""Download and store historical XAUUSD market data."""

import argparse
import logging
import time
from pathlib import Path

import pandas as pd
import yfinance as yf

from gold_pipeline.validation import find_large_gaps, find_suspicious_moves, validate_ohlc

DEFAULT_TICKER = "XAUUSD=X"
logger = logging.getLogger(__name__)


def _fetch_yahoo(ticker: str, start: str, end: str | None) -> pd.DataFrame:
    """Provider-specific call. Swap this function to change the data source."""
    return yf.download(
        ticker,
        start=start,
        end=end,
        auto_adjust=False,
        progress=False,
    )


def _normalize(raw: pd.DataFrame, ticker: str) -> pd.DataFrame:
    """Convert a provider frame to the pipeline schema: date, open, high, low, close, ..."""
    # yfinance may return MultiIndex columns, depending on its version.
    if isinstance(raw.columns, pd.MultiIndex):
        raw = raw.copy()
        raw.columns = raw.columns.get_level_values(0)

    data = raw.rename_axis("date").reset_index()
    data.columns = [str(column).lower().replace(" ", "_") for column in data.columns]

    if data.columns.duplicated().any():
        raise ValueError("Downloaded data contains duplicate column names.")

    data["ticker"] = ticker
    return data


def download_gold(
    ticker: str = DEFAULT_TICKER,
    start: str = "2020-01-01",
    end: str | None = None,
    retries: int = 3,
    backoff_seconds: float = 2.0,
) -> pd.DataFrame:
    """Download historical gold prices for `ticker`, with retries, and validate them."""
    raw = pd.DataFrame()
    for attempt in range(1, retries + 1):
        raw = _fetch_yahoo(ticker, start, end)
        if not raw.empty:
            break
        if attempt < retries:
            time.sleep(backoff_seconds * attempt)

    if raw.empty:
        raise ValueError(
            f"No data returned for {ticker!r} after {retries} attempts. "
            "Check the ticker, date range, network/VPN, yfinance version, "
            "and whether Yahoo currently serves this symbol."
        )

    # inside download_gold(), replacing the final return:
    validated = validate_ohlc(_normalize(raw, ticker))
    for name, report in (
        ("suspicious moves", find_suspicious_moves(validated)),
        ("large gaps", find_large_gaps(validated)),
    ):
        if not report.empty:
            logger.warning(
                "%s: %d rows\n%s", name, len(report), report.head().to_string(index=False)
            )
    return validated


def main() -> None:
    """Download gold data and write it to a CSV file."""
    parser = argparse.ArgumentParser(description="Download historical gold market data.")
    parser.add_argument(
        "--ticker",
        default=DEFAULT_TICKER,
        help="Yahoo ticker. XAUUSD=X is spot; GC=F is a continuous futures contract.",
    )
    parser.add_argument("--start", default="2020-01-01")
    parser.add_argument(
        "--end",
        default=None,
        help="Exclusive end date, for example 2026-01-01.",
    )
    parser.add_argument(
        "--output",
        default="data/raw/xauusd.csv",
        help="Output CSV path, relative to the current working directory.",
    )
    args = parser.parse_args()

    data = download_gold(ticker=args.ticker, start=args.start, end=args.end)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False)

    print(f"Saved {len(data)} rows ({args.ticker}) to {output_path}")
    print(f"Date range: {data['date'].min()} to {data['date'].max()}")


if __name__ == "__main__":
    main()
