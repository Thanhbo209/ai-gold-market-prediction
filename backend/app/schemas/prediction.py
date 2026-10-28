"""Response schemas for gold price predictions."""

from typing import Literal

from pydantic import BaseModel, Field


class PredictionResponse(BaseModel):
    date: str
    data_source: str
    selected_model: str
    predicted_direction: Literal[0, 1]
    predicted_label: str

    @classmethod
    def validate_direction(cls, value: int) -> int:
        if value not in (0, 1):
            raise ValueError("predicted_direction must be 0 or 1")
        return value


class PredictionHistoryResponse(BaseModel):
    """Paginated response containing historical predictions."""

    items: list[PredictionResponse]
    total: int = Field(ge=0)
    skip: int = Field(ge=0)
    limit: int = Field(gt=0)
