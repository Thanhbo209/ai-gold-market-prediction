import numpy as np
import pandas as pd
import pytest
from sklearn.dummy import DummyClassifier

from gold_pipeline.artifacts import save_model_artifact
from gold_pipeline.features import FEATURE_COLUMNS
from gold_pipeline.prediction import predict_latest_direction


@pytest.fixture
def ohlc_data() -> pd.DataFrame:
    """Create enough synthetic OHLC observations for feature warm-up."""
    dates = pd.date_range("2025-01-01", periods=100, freq="D")
    close = 2000 + np.arange(100) * 2 + np.sin(np.arange(100)) * 5

    return pd.DataFrame(
        {
            "date": dates,
            "open": close - 0.5,
            "high": close + 2,
            "low": close - 2,
            "close": close,
        }
    )


@pytest.fixture
def artifact_dir(tmp_path):
    """Save a deterministic fitted classifier and its feature metadata."""
    training_data = pd.DataFrame(
        [
            [0.01] * len(FEATURE_COLUMNS),
            [-0.01] * len(FEATURE_COLUMNS),
        ],
        columns=FEATURE_COLUMNS,
    )
    labels = [0, 1]

    model = DummyClassifier(strategy="most_frequent")
    model.fit(training_data, labels)

    directory = tmp_path / "model_artifact"
    save_model_artifact(
        model=model,
        metadata={
            "selected_model": "test_majority",
            "feature_columns": FEATURE_COLUMNS,
            "data_source": "TEST",
        },
        artifact_dir=directory,
    )
    return directory


def test_predict_latest_direction_returns_latest_prediction(
    ohlc_data,
    artifact_dir,
):
    result = predict_latest_direction(ohlc_data, artifact_dir)

    assert result["date"] == "2025-04-10"
    assert result["data_source"] == "TEST"
    assert result["selected_model"] == "test_majority"
    assert result["predicted_direction"] in (0, 1)
    assert result["predicted_label"] in ("up", "down_or_flat")


def test_predict_latest_direction_rejects_missing_artifact(ohlc_data, tmp_path):
    with pytest.raises(FileNotFoundError):
        predict_latest_direction(ohlc_data, tmp_path / "missing_artifact")


def test_predict_latest_direction_rejects_unknown_feature(
    ohlc_data,
    tmp_path,
):
    training_data = pd.DataFrame(
        [[0.0], [1.0]],
        columns=["dummy_feature"],
    )
    model = DummyClassifier(strategy="most_frequent").fit(
        training_data,
        [0, 1],
    )

    directory = tmp_path / "invalid_schema"
    save_model_artifact(
        model=model,
        metadata={
            "selected_model": "test_model",
            "feature_columns": ["unknown_feature"],
            "data_source": "TEST",
        },
        artifact_dir=directory,
    )

    with pytest.raises(ValueError, match="Missing model features"):
        predict_latest_direction(ohlc_data, directory)
