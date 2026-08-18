from decimal import Decimal

from sqlalchemy import DECIMAL, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OrderItem(Base):
    __tablename__ = "order_items"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    order_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("orders.id"),
        nullable=False,
    )

    movie_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("movies.id"),
        nullable=False,
    )

    price_at_order: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2),
        nullable=False,
    )

    order: Mapped["Order"] = relationship(
        back_populates="items",
    )

    movie: Mapped["Movie"] = relationship()
