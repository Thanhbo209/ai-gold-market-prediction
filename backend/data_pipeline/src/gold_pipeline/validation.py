"""Validation and normalization for historical OHLC market data."""

import numpy as np
import pandas as pd

REQUIRED_COLUMNS = {"date", "open", "high", "low", "close"}
PRICE_COLUMNS = ["open", "high", "low", "close"]


def _normalize_column_name(column: object) -> str:
    return str(column).strip().lower().replace(" ", "_")


def _raise_if_any(mask: pd.Series, dates: pd.Series, message: str) -> None:
    """Raise with the number of offending rows and the first few dates."""
    if mask.any():
        first = ", ".join(dates[mask].dt.strftime("%Y-%m-%d").head(5))
        raise ValueError(f"{message} ({int(mask.sum())} rows, first: {first}).")


def _normalize_dates(values: pd.Series) -> pd.Series:
    """Parse dates and return timezone-naive timestamps.

    Timezone-aware values keep their local wall-clock time, so a daily bar stamped
    2025-01-01 00:00 in New York stays on 2025-01-01 instead of shifting through UTC.
    """
    parsed = pd.to_datetime(values, errors="coerce")

    if not pd.api.types.is_datetime64_any_dtype(parsed):
        raise ValueError("Dates could not be parsed consistently (mixed timezones or formats).")

    if parsed.isna().any():
        raise ValueError(
            f"Dates contain missing or invalid values ({int(parsed.isna().sum())} rows)."
        )

    if isinstance(parsed.dtype, pd.DatetimeTZDtype):
        parsed = parsed.dt.tz_localize(None)

    return parsed


def validate_ohlc(data: pd.DataFrame) -> pd.DataFrame:
    """Validate OHLC data and return normalized, chronologically sorted rows.

    Raises ValueError on the first failed check, reporting the number of bad rows
    and the first few dates. Extra columns (volume, ticker, ...) pass through unchanged.
    """
    if data.empty:
        raise ValueError("OHLC data must not be empty.")

    result = data.copy()
    result.columns = [_normalize_column_name(column) for column in result.columns]

    if result.columns.duplicated().any():
        raise ValueError("Data contains duplicate column names.")

    # Accept a DatetimeIndex or a 'datetime' column when no date column is supplied.
    if "date" not in result.columns:
        if isinstance(result.index, pd.DatetimeIndex):
            result = result.rename_axis("date").reset_index()
        elif "datetime" in result.columns:
            result = result.rename(columns={"datetime": "date"})
        else:
            raise ValueError("Missing required date column.")

    missing_columns = REQUIRED_COLUMNS - set(result.columns)
    if missing_columns:
        raise ValueError(f"Missing required columns: {', '.join(sorted(missing_columns))}")

    result["date"] = _normalize_dates(result["date"])
    dates = result["date"]

    for column in PRICE_COLUMNS:
        result[column] = pd.to_numeric(result[column], errors="coerce")
    prices = result[PRICE_COLUMNS]

    _raise_if_any(
        prices.isna().any(axis=1),
        dates,
        "OHLC prices contain missing or nonnumeric values",
    )
    _raise_if_any(
        ~np.isfinite(prices).all(axis=1),
        dates,
        "OHLC prices must be finite numbers",
    )
    _raise_if_any(
        (prices <= 0).any(axis=1),
        dates,
        "OHLC prices must be greater than zero",
    )
    _raise_if_any(
        result["high"] < result[["open", "low", "close"]].max(axis=1),
        dates,
        "High must be greater than or equal to open, low, and close",
    )
    _raise_if_any(
        result["low"] > result[["open", "high", "close"]].min(axis=1),
        dates,
        "Low must be less than or equal to open, high, and close",
    )
    _raise_if_any(
        dates.duplicated(keep=False),
        dates,
        "Duplicate timestamps are not allowed",
    )

    return result.sort_values("date", kind="stable").reset_index(drop=True)


def find_suspicious_moves(data: pd.DataFrame, max_abs_return: float = 0.08) -> pd.DataFrame:
    """Report rows where the close-to-close move exceeds `max_abs_return`.

    Reporting only: real data can contain legitimate large moves, and futures series
    can jump at contract rolls. The 8% default is a placeholder; tune it against the
    return distribution of your actual data.
    """
    returns = data["close"].pct_change()
    mask = returns.abs() > max_abs_return
    return data.loc[mask, ["date", "close"]].assign(daily_return=returns[mask])


def find_large_gaps(data: pd.DataFrame, max_gap_days: int = 5) -> pd.DataFrame:
    """Report rows preceded by a calendar gap longer than `max_gap_days`.

    Expects validated (sorted) data. Weekends and most holidays fall under the default.
    """
    gap_days = data["date"].diff().dt.days
    mask = gap_days > max_gap_days
    return data.loc[mask, ["date"]].assign(gap_days=gap_days[mask])
