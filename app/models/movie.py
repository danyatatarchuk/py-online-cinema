import uuid
from decimal import Decimal

from sqlalchemy import (
    DECIMAL,
    Column,
    Float,
    ForeignKey,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
)
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


movie_genres = Table(
    "movie_genres",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("genre_id", ForeignKey("genres.id"), primary_key=True),
)


movie_stars = Table(
    "movie_stars",
    Base.metadata,
    Column("movie_id", ForeignKey("movies.id"), primary_key=True),
    Column("star_id", ForeignKey("stars.id"), primary_key=True),
)


class Movie(Base):
    __tablename__ = "movies"

    __table_args__ = (
        UniqueConstraint("name", "year", "time"),
    )

    id: Mapped[int] = mapped_column(Integer, primary_key=True)
    uuid: Mapped[uuid.UUID] = mapped_column(
        default=uuid.uuid4,
        unique=True,
        nullable=False,
    )
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    year: Mapped[int] = mapped_column(Integer, nullable=False)
    time: Mapped[int] = mapped_column(Integer, nullable=False)
    imdb: Mapped[float] = mapped_column(Float, nullable=False)
    votes: Mapped[int] = mapped_column(Integer, nullable=False)
    meta_score: Mapped[float | None] = mapped_column(Float, nullable=True)
    gross: Mapped[float | None] = mapped_column(Float, nullable=True)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    price: Mapped[Decimal] = mapped_column(
        DECIMAL(10, 2),
        nullable=False,
    )
    certification_id: Mapped[int] = mapped_column(
        Integer,
        ForeignKey("certifications.id"),
        nullable=False,
    )
