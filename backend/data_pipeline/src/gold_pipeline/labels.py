"""Construct next-observation return and direction labels."""

import pandas as pd

LABEL_COLUMNS = ["target_return", "target_direction"]


def build_labels(data: pd.DataFrame) -> pd.DataFrame:
    """Return date-aligned next-observation labels, excluding the final row."""
    if data.empty:
        raise ValueError("Cannot build labels from empty data.")

    if "date" not in data.columns or "close" not in data.columns:
        raise ValueError("Input must contain date and close columns.")

    result = data[["date", "close"]].copy()
    result["date"] = pd.to_datetime(result["date"], errors="coerce")

    if result["date"].isna().any():
        raise ValueError("Dates contain missing or invalid values.")

    if result["date"].duplicated().any():
        raise ValueError("Duplicate dates are not allowed.")

    if not result["date"].is_monotonic_increasing:
        raise ValueError("Dates must be sorted in ascending order.")

    result["close"] = pd.to_numeric(result["close"], errors="coerce")

    if result["close"].isna().any() or (result["close"] <= 0).any():
        raise ValueError("Close prices must be numeric and greater than zero.")

    result["target_return"] = result["close"].shift(-1).div(result["close"]) - 1
    result["target_direction"] = (result["target_return"] > 0).astype("int8")

    # The last row has no known next-observation return.
    result = result.iloc[:-1]

    return result[["date", *LABEL_COLUMNS]].reset_index(drop=True)
