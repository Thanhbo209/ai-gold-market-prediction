"""Download and store historical XAUUSD market data."""

import argparse
from pathlib import Path

import pandas as pd
import yfinance as yf


def download_xauusd(
        start: str = "2020-01-01",
        end: str | None = None
) -> pd.DataFrame:
    """Download historical XAUUSD data and normalize its columns."""
    raw = yf.dowload(
        "XAUUSD=X",
        start=start,
        end=end,
        auto_adjust=False,
        progress=False,
    )

    # Validate for empty case
    if raw.empty:
        raise ValueError(
            "No XAUUSD data returned. Check the ticker, date range, "
            "network connection, and data provider availability."
        )

    # yfinance may return MultiIndex columns, depending on its version.
    if isinstance(raw.columns, pd.MultiIndex):
        raw.columns = raw.columns.get_level_values(0)

    data = raw.rename_axis("date").reset_index()
    data.columns = [str(column).lower() for column in data.columns]

    # Remove duplicate column names if normalization created any.
    if data.columns.duplicated().any():
        raise ValueError("Downloaded data contains duplicate column names.")

     # Step 3 will provide the shared OHLC validation function.
    from gold_pipeline.validation import validate_ohlc

    return validate_ohlc(data)


def main() -> None:
    """Download XAUUSD data and write it to a CSV file."""
    parser = argparse.ArgumentParser(
        description="Download historical XAUUSD market data."
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

    data = download_xauusd(start=args.start, end=args.end)

    output_path = Path(args.output)
    output_path.parent.mkdir(parents=True, exist_ok=True)
    data.to_csv(output_path, index=False)

    print(f"Saved {len(data)} rows to {output_path}")
    print(f"Date range: {data['date'].min()} to {data['date'].max()}")


if __name__ == "__main__":
    main()