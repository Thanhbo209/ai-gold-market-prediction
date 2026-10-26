"""Save and reload trained models with experiment metadata."""

import json
from pathlib import Path
from typing import Any

import joblib

ARTIFACT_VERSION = 1
MODEL_FILENAME = "model.joblib"
METADATA_FILENAME = "metadata.json"


def save_model_artifact(
    model: Any,
    metadata: dict[str, Any],
    artifact_dir: str | Path,
) -> dict[str, Path]:
    """Save a fitted model and JSON metadata to an artifact directory."""
    if not isinstance(metadata, dict):
        raise ValueError("Metadata must be a dictionary.")

    if not metadata.get("feature_columns"):
        raise ValueError("Metadata must include feature_columns.")

    directory = Path(artifact_dir)
    directory.mkdir(parents=True, exist_ok=True)

    model_path = directory / MODEL_FILENAME
    metadata_path = directory / METADATA_FILENAME

    document = {
        **metadata,
        "artifact_version": ARTIFACT_VERSION,
        "model_class": (f"{type(model).__module__}.{type(model).__qualname__}"),
    }

    # Validate JSON serializability before writing either artifact.
    serialized_metadata = json.dumps(document, indent=2, sort_keys=True)

    joblib.dump(model, model_path)
    metadata_path.write_text(
        serialized_metadata + "\n",
        encoding="utf-8",
    )

    return {
        "model_path": model_path,
        "metadata_path": metadata_path,
    }


def load_model_artifact(
    artifact_dir: str | Path,
) -> tuple[Any, dict[str, Any]]:
    """Load a saved model and validate its metadata version."""
    directory = Path(artifact_dir)
    model_path = directory / MODEL_FILENAME
    metadata_path = directory / METADATA_FILENAME

    if not model_path.is_file() or not metadata_path.is_file():
        raise FileNotFoundError("Model artifact or metadata file is missing.")

    metadata = json.loads(metadata_path.read_text(encoding="utf-8"))

    if metadata.get("artifact_version") != ARTIFACT_VERSION:
        raise ValueError("Unsupported artifact version.")

    if not metadata.get("feature_columns"):
        raise ValueError("Artifact metadata is missing feature_columns.")

    model = joblib.load(model_path)
    return model, metadata
