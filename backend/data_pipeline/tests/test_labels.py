"""Tests for next-observation labels."""

import pandas as pd
import pytest

from gold_pipeline.labels import build_labels


@pytest.fixture
def sample_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2025-01-01", periods=4, freq="D"),
            "close": [100.0, 105.0, 99.75, 109.725],
        }
    )


def test_labels_equal_next_observation_returns(sample_data: pd.DataFrame) -> None:
    labels = build_labels(sample_data)

    expected = [0.05, -0.05, 0.10]
    assert labels["target_return"].tolist() == pytest.approx(expected)


def test_final_row_is_dropped(sample_data: pd.DataFrame) -> None:
    labels = build_labels(sample_data)

    assert len(labels) == len(sample_data) - 1
    assert labels["date"].iloc[-1] == pd.Timestamp("2025-01-03")


def test_direction_labels(sample_data: pd.DataFrame) -> None:
    labels = build_labels(sample_data)

    assert labels["target_direction"].tolist() == [1, 0, 1]


def test_label_output_contains_only_date_and_targets(
    sample_data: pd.DataFrame,
) -> None:
    labels = build_labels(sample_data)

    assert labels.columns.tolist() == [
        "date",
        "target_return",
        "target_direction",
    ]


def test_unsorted_dates_are_rejected(sample_data: pd.DataFrame) -> None:
    data = sample_data.iloc[::-1].reset_index(drop=True)

    with pytest.raises(ValueError, match="sorted"):
        build_labels(data)


def test_duplicate_dates_are_rejected(sample_data: pd.DataFrame) -> None:
    sample_data.loc[1, "date"] = sample_data.loc[0, "date"]

    with pytest.raises(ValueError, match="Duplicate dates"):
        build_labels(sample_data)


def test_nonpositive_close_is_rejected(sample_data: pd.DataFrame) -> None:
    sample_data.loc[1, "close"] = 0

    with pytest.raises(ValueError, match="greater than zero"):
        build_labels(sample_data)
