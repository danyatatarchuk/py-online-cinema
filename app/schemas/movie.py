from decimal import Decimal
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class MovieResponse(BaseModel):
    id: int
    uuid: UUID
    name: str
    year: int
    time: int
    imdb: float
    votes: int
    meta_score: float | None
    gross: float | None
    description: str
    price: Decimal
    certification_id: int

    model_config = ConfigDict(from_attributes=True)
