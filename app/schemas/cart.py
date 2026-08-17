from decimal import Decimal

from pydantic import BaseModel


class CartItemResponse(BaseModel):
    id: int
    movie_id: int
    movie_name: str
    price: Decimal
