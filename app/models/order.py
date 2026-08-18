from datetime import datetime
from decimal import Decimal
from enum import Enum

from sqlalchemy import DECIMAL, DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class OrderStatus(str, Enum):
    PENDING = "pending"
    PAID = "paid"
    CANCELED = "canceled"


class Order(Base):
    __tablename__ = "orders"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        nullable=False,
    )

    created_at: Mapped[datetime] = mapped_column(
        DateTime,
        default=datetime.utcnow,
        nullable=False,
    )

    status: Mapped[OrderStatus] = mapped_column(
        String(50),
        default=OrderStatus.PENDING,
        nullable=False,
    )

    total_amount: Mapped[Decimal | None] = mapped_column(
        DECIMAL(10, 2),
        nullable=True,
    )

    items: Mapped[list["OrderItem"]] = relationship(
        back_populates="order",
        cascade="all, delete-orphan",
    )
