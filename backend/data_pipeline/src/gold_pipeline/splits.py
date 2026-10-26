"""Chronological dataset splitting with an optional observation gap."""

import pandas as pd


def chronological_split(
    data: pd.DataFrame,
    train_end: str | pd.Timestamp,
    val_end: str | pd.Timestamp,
    gap: int = 1,
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """Split data chronologically, leaving gap observations between each set."""
    if "date" not in data.columns:
        raise ValueError("Input must contain a date column.")

    if data.empty:
        raise ValueError("Cannot split empty data.")

    if not isinstance(gap, int) or isinstance(gap, bool) or gap < 0:
        raise ValueError("gap must be a non-negative integer.")

    dates = pd.to_datetime(data["date"], errors="coerce")

    if dates.isna().any():
        raise ValueError("Dates contain missing or invalid values.")

    if dates.duplicated().any():
        raise ValueError("Duplicate dates are not allowed.")

    if not dates.is_monotonic_increasing:
        raise ValueError("Dates must be sorted in ascending order.")

    train_boundary = pd.Timestamp(train_end)
    validation_boundary = pd.Timestamp(val_end)

    if train_boundary >= validation_boundary:
        raise ValueError("train_end must be earlier than val_end.")

    train = data.loc[dates <= train_boundary].copy()
    validation = data.loc[(dates > train_boundary) & (dates <= validation_boundary)].copy()
    test = data.loc[dates > validation_boundary].copy()

    if len(train) <= gap:
        raise ValueError("Training set is too small for the requested gap.")

    if len(validation) <= gap:
        raise ValueError("Validation set is too small for the requested gap.")

    # Leave `gap` observations unused at each split boundary.
    if gap:
        train = train.iloc[:-gap]
        validation = validation.iloc[:-gap]

    if train.empty or validation.empty or test.empty:
        raise ValueError("Train, validation, and test sets must all be non-empty.")

    return (
        train.reset_index(drop=True),
        validation.reset_index(drop=True),
        test.reset_index(drop=True),
    )
