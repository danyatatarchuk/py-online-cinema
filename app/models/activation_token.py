from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class ActivationToken(Base):
    __tablename__ = "activation_tokens"

    id: Mapped[int] = mapped_column(
        Integer,
        primary_key=True,
    )

    user_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("users.id"),
        unique=True,
        nullable=False,
    )

    token: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    expires_at: Mapped[datetime] = mapped_column(
        DateTime,
        nullable=False,
    )

    user: Mapped["User"] = relationship(
        back_populates="activation_token",
    )
