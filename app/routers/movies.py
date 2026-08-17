from fastapi import APIRouter, Depends, Query
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.movie import Movie
from app.schemas.movie import MovieResponse


router = APIRouter(
    prefix="/movies",
    tags=["Movies"],
)


@router.get(
    "",
    response_model=list[MovieResponse],
    summary="Get movies",
    description="Returns a paginated list of movies with filtering and sorting.",
)
async def get_movies(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    year: int | None = None,
    min_rating: float | None = Query(None, ge=0, le=10),
    max_rating: float | None = Query(None, ge=0, le=10),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    sort_by: str | None = Query(None),
    order: str = Query("asc"),
    db: AsyncSession = Depends(get_db),
):
    query = select(Movie)

    if year is not None:
        query = query.where(Movie.year == year)

    if min_rating is not None:
        query = query.where(Movie.imdb >= min_rating)

    if max_rating is not None:
        query = query.where(Movie.imdb <= max_rating)

    if min_price is not None:
        query = query.where(Movie.price >= min_price)

    if max_price is not None:
        query = query.where(Movie.price <= max_price)

    sort_fields = {
        "year": Movie.year,
        "imdb": Movie.imdb,
        "price": Movie.price,
    }

    if sort_by in sort_fields:
        sort_field = sort_fields[sort_by]

        if order.lower() == "desc":
            query = query.order_by(sort_field.desc())
        else:
            query = query.order_by(sort_field.asc())

    offset = (page - 1) * per_page

    result = await db.execute(
        query
        .offset(offset)
        .limit(per_page)
    )

    return result.scalars().all()
