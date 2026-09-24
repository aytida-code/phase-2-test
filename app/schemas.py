"""Response schemas."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class LetterOut(BaseModel):
    """A persisted randomly generated letter."""

    id: int
    value: str
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
