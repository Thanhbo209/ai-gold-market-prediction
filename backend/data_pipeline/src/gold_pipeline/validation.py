"""Validation and normalization for historical OHLC market data."""

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {"date", "open", "high", "low", "close"}
PRICE_COLUMNS = ["open", "high", "low", "close"]


def validate_ohlc(data: pd.DataFrame) -> pd.DataFrame:
    """Validate OHLC data and return normalized, chronologically sorted rows."""
    if data.empty:
        raise ValueError("OHLC data must not be empty.")

    result = data.copy()
    result.columns = [str(column).strip().lower() for column in result.columns]

    if result.columns.duplicated().any():
        raise ValueError("Data contains duplicate column names.")

    # Accept a DatetimeIndex when no date column is supplied.
    if "date" not in result.columns:
        if isinstance(result.index, pd.DatetimeIndex):
            result.index.name = "date"
            result = result.reset_index()
        elif "datetime" in result.columns:
            result = result.rename(columns={"datetime": "date"})
        elif "index" in result.columns and isinstance(result["index"].dtype, pd.DatetimeTZDtype):
            result = result.rename(columns={"index": "date"})
        else:
            raise ValueError("Missing required date column.")

    missing_columns = REQUIRED_COLUMNS - set(result.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing_columns))}")

    # Normalize dates to UTC, then store them as timezone-naive UTC timestamps.
    result["date"] = pd.to_datetime(result["date"], errors="coerce", utc=True)

    if result["date"].isna().any():
        raise ValueError("Dates contain missing or invalid values.")

    result["date"] = result["date"].dt.tz_localize(None)

    # Ensure OHLC values are numeric.
    for column in PRICE_COLUMNS:
        result[column] = pd.to_numeric(result[column], errors="coerce")

    if result[PRICE_COLUMNS].isna().any().any():
        raise ValueError("OHLC prices contain missing or nonnumeric values.")

    if not np.isfinite(result[PRICE_COLUMNS].to_numpy()).all():
        raise ValueError("OHLC prices must be finite numbers.")

    if (result[PRICE_COLUMNS] <= 0).any().any():
        raise ValueError("OHLC prices must be greater than zero.")

    # The high must be the greatest price; the low must be the smallest.
    other_columns = ["open", "low", "close"]
    if (result["high"] < result[other_columns].max(axis=1)).any():
        raise ValueError("High must be greater than or equal to open, low, and close.")

    other_columns = ["open", "high", "close"]
    if (result["low"] > result[other_columns].min(axis=1)).any():
        raise ValueError("Low must be less than or equal to open, high, and close.")

    if result["date"].duplicated().any():
        raise ValueError("Duplicate timestamps are not allowed.")

    return result.sort_values("date").reset_index(drop=True)
