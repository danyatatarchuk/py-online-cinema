from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class CartItem(Base):
    __tablename__ = "cart_items"

    __table_args__ = (
        UniqueConstraint("cart_id", "movie_id"),
    )

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    cart_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("carts.id"),
        nullable=False,
    )

    movie_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("movies.id"),
        nullable=False,
    )

    added_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    cart: Mapped["Cart"] = relationship(
        back_populates="items",
    )

    movie: Mapped["Movie"] = relationship()
