"""Tests for feature generation and future invariance."""

import numpy as np
import pandas as pd
import pytest

from gold_pipeline.features import FEATURE_COLUMNS, build_features


@pytest.fixture
def sample_data() -> pd.DataFrame:
    periods = 80
    dates = pd.date_range("2025-01-01", periods=periods, freq="D")

    # Deterministic synthetic prices: no network calls or external data required.
    close = 2500 + np.arange(periods) * 1.5 + np.sin(np.arange(periods) / 3) * 8
    open_price = close * (1 + np.sin(np.arange(periods)) * 0.001)

    return pd.DataFrame(
        {
            "date": dates,
            "open": open_price,
            "high": np.maximum(open_price, close) * 1.002,
            "low": np.minimum(open_price, close) * 0.998,
            "close": close,
        }
    )


def test_warmup_drops_first_49_rows(sample_data: pd.DataFrame) -> None:
    features = build_features(sample_data)

    assert len(features) == len(sample_data) - 49
    assert features["date"].iloc[0] == sample_data["date"].iloc[49]


def test_features_have_no_missing_values_after_warmup(
    sample_data: pd.DataFrame,
) -> None:
    features = build_features(sample_data)

    assert not features[FEATURE_COLUMNS].isna().any().any()


def test_feature_columns_have_fixed_order(sample_data: pd.DataFrame) -> None:
    features = build_features(sample_data)

    assert features.columns.tolist() == ["date", *FEATURE_COLUMNS]


def test_output_does_not_include_labels(sample_data: pd.DataFrame) -> None:
    sample_data["target_return"] = 0.01
    sample_data["target_direction"] = 1

    features = build_features(sample_data)

    assert "target_return" not in features.columns
    assert "target_direction" not in features.columns


@pytest.mark.parametrize("position", [50, 55, 65, 79])
def test_features_are_invariant_to_future_data(
    sample_data: pd.DataFrame,
    position: int,
) -> None:
    full_features = build_features(sample_data)

    truncated_data = sample_data.iloc[: position + 1].copy()
    truncated_features = build_features(truncated_data)

    target_date = sample_data["date"].iloc[position]

    full_row = full_features.loc[full_features["date"] == target_date, FEATURE_COLUMNS]
    truncated_row = truncated_features.loc[
        truncated_features["date"] == target_date,
        FEATURE_COLUMNS,
    ]

    assert len(full_row) == 1
    assert len(truncated_row) == 1

    pd.testing.assert_frame_equal(
        full_row.reset_index(drop=True),
        truncated_row.reset_index(drop=True),
    )


def test_unsorted_dates_are_rejected(sample_data: pd.DataFrame) -> None:
    data = sample_data.iloc[::-1].reset_index(drop=True)

    with pytest.raises(ValueError, match="sorted"):
        build_features(data)


def test_duplicate_dates_are_rejected(sample_data: pd.DataFrame) -> None:
    sample_data.loc[1, "date"] = sample_data.loc[0, "date"]

    with pytest.raises(ValueError, match="Duplicate dates"):
        build_features(sample_data)
