"""Tests for OHLC data validation."""

import pandas as pd
import pytest

from gold_pipeline.validation import find_large_gaps, find_suspicious_moves, validate_ohlc


@pytest.fixture
def valid_data() -> pd.DataFrame:
    # Deliberately unsorted, so sorting is exercised by every test.
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


# --- Happy path ---------------------------------------------------------------------


def test_valid_data_is_sorted_chronologically(valid_data: pd.DataFrame) -> None:
    result = validate_ohlc(valid_data)

    assert result["date"].is_monotonic_increasing
    assert result["date"].iloc[0] == pd.Timestamp("2025-01-01")
    assert result.index.equals(pd.RangeIndex(len(result)))


def test_extra_columns_pass_through(valid_data: pd.DataFrame) -> None:
    valid_data["ticker"] = "GC=F"

    result = validate_ohlc(valid_data)

    assert {"volume", "ticker"} <= set(result.columns)
    assert (result["ticker"] == "GC=F").all()


def test_input_is_not_mutated(valid_data: pd.DataFrame) -> None:
    before = valid_data.copy()

    validate_ohlc(valid_data)

    pd.testing.assert_frame_equal(valid_data, before)


def test_column_names_are_normalized(valid_data: pd.DataFrame) -> None:
    data = valid_data.rename(columns={"close": " Close ", "volume": "Adj Close"})

    result = validate_ohlc(data)

    assert "close" in result.columns
    assert "adj_close" in result.columns


# --- Date handling ------------------------------------------------------------------


def test_datetime_index_is_supported() -> None:
    data = pd.DataFrame(
        {"open": [2600.0], "high": [2620.0], "low": [2590.0], "close": [2610.0]},
        index=pd.DatetimeIndex(["2025-01-01"], name="Date"),
    )

    result = validate_ohlc(data)

    assert "date" in result.columns
    assert result.loc[0, "close"] == 2610.0


def test_timezone_aware_dates_keep_calendar_date() -> None:
    data = pd.DataFrame(
        {"open": [2600.0], "high": [2620.0], "low": [2590.0], "close": [2610.0]},
        index=pd.DatetimeIndex(["2025-01-01"], tz="America/New_York", name="Date"),
    )

    result = validate_ohlc(data)

    assert result["date"].dt.tz is None
    assert result.loc[0, "date"] == pd.Timestamp("2025-01-01")


def test_invalid_date_is_rejected(valid_data: pd.DataFrame) -> None:
    valid_data.loc[1, "date"] = "not-a-date"

    with pytest.raises(ValueError, match="missing or invalid"):
        validate_ohlc(valid_data)


def test_duplicate_timestamps_are_rejected(valid_data: pd.DataFrame) -> None:
    valid_data.loc[1, "date"] = valid_data.loc[0, "date"]

    with pytest.raises(ValueError, match="Duplicate timestamps"):
        validate_ohlc(valid_data)


# --- Structure ----------------------------------------------------------------------


def test_empty_data_is_rejected(valid_data: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="must not be empty"):
        validate_ohlc(valid_data.iloc[0:0])


def test_missing_required_column_is_rejected(valid_data: pd.DataFrame) -> None:
    data = valid_data.drop(columns=["close"])

    with pytest.raises(ValueError, match="Missing required columns"):
        validate_ohlc(data)


def test_missing_date_is_rejected(valid_data: pd.DataFrame) -> None:
    data = valid_data.drop(columns=["date"])

    with pytest.raises(ValueError, match="Missing required date column"):
        validate_ohlc(data)


def test_duplicate_column_names_are_rejected(valid_data: pd.DataFrame) -> None:
    # "Close" and "close" collide once names are lowercased.
    data = valid_data.rename(columns={"open": "Close"})

    with pytest.raises(ValueError, match="duplicate column names"):
        validate_ohlc(data)


# --- Prices -------------------------------------------------------------------------


def test_missing_price_is_rejected(valid_data: pd.DataFrame) -> None:
    valid_data.loc[0, "close"] = float("nan")

    with pytest.raises(ValueError, match="missing or nonnumeric"):
        validate_ohlc(valid_data)


def test_nonnumeric_price_is_rejected(valid_data: pd.DataFrame) -> None:
    valid_data["open"] = valid_data["open"].astype(object)
    valid_data.loc[0, "open"] = "not-a-price"

    with pytest.raises(ValueError, match="missing or nonnumeric"):
        validate_ohlc(valid_data)


def test_infinite_price_is_rejected(valid_data: pd.DataFrame) -> None:
    valid_data.loc[0, "high"] = float("inf")

    with pytest.raises(ValueError, match="finite"):
        validate_ohlc(valid_data)


@pytest.mark.parametrize("bad_value", [0.0, -1.0])
def test_nonpositive_price_is_rejected(valid_data: pd.DataFrame, bad_value: float) -> None:
    valid_data.loc[0, "low"] = bad_value

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


def test_error_message_reports_count_and_first_date(valid_data: pd.DataFrame) -> None:
    valid_data.loc[0, "high"] = 2645.0  # row dated 2025-01-02

    with pytest.raises(ValueError, match=r"1 rows, first: 2025-01-02"):
        validate_ohlc(valid_data)


# --- Reporting helpers --------------------------------------------------------------


def test_find_suspicious_moves_flags_only_large_moves() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-01", "2025-01-02", "2025-01-03"]),
            "close": [100.0, 101.0, 120.0],
        }
    )

    result = find_suspicious_moves(data, max_abs_return=0.08)

    assert result["date"].tolist() == [pd.Timestamp("2025-01-03")]


def test_find_large_gaps_ignores_weekends() -> None:
    data = pd.DataFrame(
        {
            "date": pd.to_datetime(["2025-01-03", "2025-01-06", "2025-01-24"]),  # Fri, Mon, +18d
        }
    )

    result = find_large_gaps(data, max_gap_days=5)

    assert result["date"].tolist() == [pd.Timestamp("2025-01-24")]
    assert result["gap_days"].tolist() == [18]
