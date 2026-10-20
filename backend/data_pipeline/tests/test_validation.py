"""Tests for OHLC data validation."""

import pandas as pd
import pytest

from gold_pipeline.validation import validate_ohlc


@pytest.fixture
def valid_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": ["2025-01-02", "2025-01-01"],
            "open": [2650.0, 2600.0],
            "high": [2670.0, 2620.0],
            "low": [2640.0, 2590.0],
            "close": [2660.0, 2610.0],
            "volume": [100, 120],
        }
    )


def test_valid_data_is_sorted_chronologically(valid_data: pd.DataFrame) -> None:
    result = validate_ohlc(valid_data)

    assert result["date"].is_monotonic_increasing
    assert result["date"].iloc[0] == pd.Timestamp("2025-01-01")
    assert "volume" in result.columns


def test_missing_required_column_is_rejected(valid_data: pd.DataFrame) -> None:
    data = valid_data.drop(columns=["close"])

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_ohlc(data)


def test_missing_price_is_rejected(valid_data: pd.DataFrame) -> None:
    valid_data.loc[0, "close"] = float("nan")

    with pytest.raises(ValueError, match="missing or nonnumeric"):
        validate_ohlc(valid_data)


def test_nonnumeric_price_is_rejected(valid_data: pd.DataFrame) -> None:
    valid_data["open"] = valid_data["open"].astype(object)
    valid_data.loc[0, "open"] = "not-a-price"

    with pytest.raises(ValueError, match="missing or nonnumeric"):
        validate_ohlc(valid_data)


def test_duplicate_timestamps_are_rejected(valid_data: pd.DataFrame) -> None:
    valid_data.loc[1, "date"] = valid_data.loc[0, "date"]

    with pytest.raises(ValueError, match="Duplicate timestamps"):
        validate_ohlc(valid_data)


def test_nonpositive_price_is_rejected(valid_data: pd.DataFrame) -> None:
    valid_data.loc[0, "low"] = 0

    with pytest.raises(ValueError, match="greater than zero"):
        validate_ohlc(valid_data)


def test_invalid_high_is_rejected(valid_data: pd.DataFrame) -> None:
    valid_data.loc[0, "high"] = 2645.0

    with pytest.raises(ValueError, match="High must be"):
        validate_ohlc(valid_data)


def test_invalid_low_is_rejected(valid_data: pd.DataFrame) -> None:
    valid_data.loc[0, "low"] = 2665.0

    with pytest.raises(ValueError, match="Low must be"):
        validate_ohlc(valid_data)


def test_datetime_index_is_supported() -> None:
    data = pd.DataFrame(
        {
            "open": [2600.0],
            "high": [2620.0],
            "low": [2590.0],
            "close": [2610.0],
        },
        index=pd.DatetimeIndex(["2025-01-01"], name="Date"),
    )

    result = validate_ohlc(data)

    assert "date" in result.columns
    assert result.loc[0, "close"] == 2610.0
