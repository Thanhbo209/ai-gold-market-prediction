"""Tests for chronological data splitting."""

import pandas as pd
import pytest

from gold_pipeline.splits import chronological_split


@pytest.fixture
def sample_data() -> pd.DataFrame:
    return pd.DataFrame(
        {
            "date": pd.date_range("2025-01-01", periods=30, freq="D"),
            "value": range(30),
        }
    )


def test_splits_are_chronological_and_disjoint(
    sample_data: pd.DataFrame,
) -> None:
    train, validation, test = chronological_split(
        sample_data,
        train_end="2025-01-11",
        val_end="2025-01-21",
        gap=2,
    )

    assert train["date"].max() < validation["date"].min()
    assert validation["date"].max() < test["date"].min()

    assert set(train["date"]).isdisjoint(validation["date"])
    assert set(train["date"]).isdisjoint(test["date"])
    assert set(validation["date"]).isdisjoint(test["date"])


def test_gap_observations_are_left_out(sample_data: pd.DataFrame) -> None:
    train, validation, test = chronological_split(
        sample_data,
        train_end="2025-01-11",
        val_end="2025-01-21",
        gap=2,
    )

    all_dates = sample_data["date"].tolist()
    train_last = all_dates.index(train["date"].iloc[-1])
    validation_first = all_dates.index(validation["date"].iloc[0])
    validation_last = all_dates.index(validation["date"].iloc[-1])
    test_first = all_dates.index(test["date"].iloc[0])

    assert validation_first - train_last - 1 >= 2
    assert test_first - validation_last - 1 >= 2


def test_zero_gap_is_allowed(sample_data: pd.DataFrame) -> None:
    train, validation, test = chronological_split(
        sample_data,
        train_end="2025-01-10",
        val_end="2025-01-20",
        gap=0,
    )

    assert not train.empty
    assert not validation.empty
    assert not test.empty


def test_unsorted_dates_are_rejected(sample_data: pd.DataFrame) -> None:
    data = sample_data.iloc[::-1].reset_index(drop=True)

    with pytest.raises(ValueError, match="sorted"):
        chronological_split(data, "2025-01-10", "2025-01-20")


def test_duplicate_dates_are_rejected(sample_data: pd.DataFrame) -> None:
    sample_data.loc[1, "date"] = sample_data.loc[0, "date"]

    with pytest.raises(ValueError, match="Duplicate dates"):
        chronological_split(sample_data, "2025-01-10", "2025-01-20")


def test_invalid_boundaries_are_rejected(sample_data: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="earlier"):
        chronological_split(sample_data, "2025-01-20", "2025-01-10")


def test_negative_gap_is_rejected(sample_data: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="non-negative"):
        chronological_split(sample_data, "2025-01-10", "2025-01-20", gap=-1)


def test_too_small_split_is_rejected(sample_data: pd.DataFrame) -> None:
    with pytest.raises(ValueError, match="too small"):
        chronological_split(
            sample_data,
            train_end="2025-01-02",
            val_end="2025-01-20",
            gap=2,
        )
