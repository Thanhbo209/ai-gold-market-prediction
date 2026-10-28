
from unittest.mock import patch

import pytest

from app.services import prediction


@pytest.fixture
def prediction_csv(tmp_path, monkeypatch):
    csv_path = tmp_path / "gold.csv"
    csv_path.write_text(
        "date,open,high,low,close,volume\n"
        "2026-10-27,1,2,0.5,1.5,100\n",
        encoding="utf-8",
    )
    monkeypatch.setattr(prediction, "DATA_PATH", csv_path)
    return csv_path

@pytest.fixture
def mock_prediction():
    with patch(
        "app.services.prediction.predict_latest_direction"
    ) as mock:
        mock.return_value = {
            "date": "2026-10-27",
            "data_source": "GC=F",
            "selected_model": "majority",
            "predicted_direction": 1,
            "predicted_label": "up",
        }
        yield mock


def test_get_latest_prediction_returns_prediction(mock_prediction, prediction_csv):
    result = prediction.get_latest_prediction()

    assert result["predicted_label"] == "up"
    assert result["predicted_direction"] == 1
    assert result["data_source"] == "GC=F"
    mock_prediction.assert_called_once()


def test_get_latest_prediction_passes_loaded_data_and_artifact_path(
    mock_prediction,
    prediction_csv
):
    result = prediction.get_latest_prediction()

    args = mock_prediction.call_args.kwargs
    assert not args["data"].empty
    assert args["artifact_dir"] == prediction.ARTIFACT_DIR
    assert result["date"] == "2026-10-27"


def test_get_latest_prediction_raises_when_data_is_missing(
    mock_prediction, monkeypatch
):
    monkeypatch.setattr(
        prediction, "DATA_PATH", prediction.DATA_PATH / "missing.csv"
    )

    with pytest.raises(FileNotFoundError, match="Historical data not found"):
        prediction.get_latest_prediction()

    mock_prediction.assert_not_called()


def test_get_latest_prediction_raises_when_artifacts_are_missing(
    mock_prediction, monkeypatch, tmp_path
):
    monkeypatch.setattr(prediction, "ARTIFACT_DIR", tmp_path / "missing")

    with pytest.raises(FileNotFoundError, match="Model artifacts not found"):
        prediction.get_latest_prediction()

    mock_prediction.assert_not_called()
