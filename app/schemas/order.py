from datetime import datetime
from decimal import Decimal

from pydantic import BaseModel


class OrderItemResponse(BaseModel):
    id: int
    movie_id: int
    movie_name: str
    price_at_order: Decimal


class OrderResponse(BaseModel):
    id: int
    created_at: datetime
    status: str
    total_amount: Decimal
    items: list[OrderItemResponse]
