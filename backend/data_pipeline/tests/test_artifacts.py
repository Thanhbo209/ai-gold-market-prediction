"""Tests for model artifact persistence."""

import json

import numpy as np
import pandas as pd
import pytest
from sklearn.dummy import DummyClassifier

from gold_pipeline.artifacts import (
    ARTIFACT_VERSION,
    load_model_artifact,
    save_model_artifact,
)


def make_fitted_model() -> tuple[DummyClassifier, pd.DataFrame]:
    features = pd.DataFrame(
        {
            "return_1": [-0.1, 0.1, -0.2, 0.2],
            "volatility_5": [0.01, 0.02, 0.03, 0.04],
        }
    )
    labels = pd.Series([0, 1, 0, 1])

    model = DummyClassifier(strategy="most_frequent")
    model.fit(features, labels)
    return model, features


def test_saved_model_reproduces_predictions(tmp_path):
    model, features = make_fitted_model()
    expected = model.predict(features)

    metadata = {
        "feature_columns": ["return_1", "volatility_5"],
        "data_source": "GC=F",
        "selected_model": "majority",
        "date_ranges": {
            "train_start": "2020-01-01",
            "train_end": "2020-06-30",
        },
        "metrics": {"validation_accuracy": 0.55},
    }

    paths = save_model_artifact(model, metadata, tmp_path / "artifact")
    loaded_model, loaded_metadata = load_model_artifact(tmp_path / "artifact")

    actual = loaded_model.predict(features)

    np.testing.assert_array_equal(actual, expected)
    assert loaded_metadata["artifact_version"] == ARTIFACT_VERSION
    assert loaded_metadata["feature_columns"] == metadata["feature_columns"]
    assert loaded_metadata["data_source"] == "GC=F"
    assert paths["model_path"].is_file()
    assert paths["metadata_path"].is_file()


def test_save_requires_feature_columns(tmp_path):
    model, _ = make_fitted_model()

    with pytest.raises(ValueError, match="feature_columns"):
        save_model_artifact(model, {"data_source": "GC=F"}, tmp_path)


def test_load_rejects_unsupported_artifact_version(tmp_path):
    model, _ = make_fitted_model()
    directory = tmp_path / "artifact"
    save_model_artifact(
        model,
        {"feature_columns": ["return_1"]},
        directory,
    )

    metadata_path = directory / "metadata.json"
    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))
    metadata["artifact_version"] = 999
    metadata_path.write_text(json.dumps(metadata), encoding="utf-8")

    with pytest.raises(ValueError, match="Unsupported artifact version"):
        load_model_artifact(directory)


def test_load_rejects_missing_artifact_files(tmp_path):
    with pytest.raises(FileNotFoundError, match="missing"):
        load_model_artifact(tmp_path / "does-not-exist")
