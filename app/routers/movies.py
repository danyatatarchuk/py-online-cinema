from fastapi import APIRouter, Depends, Query
from sqlalchemy import asc, desc, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.models.director import Director
from app.models.movie import Movie, movie_directors, movie_stars
from app.models.star import Star
from app.schemas.movie import MovieResponse


router = APIRouter(
    prefix="/movies",
    tags=["Movies"],
)


@router.get(
    "",
    response_model=list[MovieResponse],
    summary="Get movies",
    description=(
        "Returns a paginated list of movies with filtering, sorting, "
        "and search by movie name, star, or director."
    ),
)
async def get_movies(
    page: int = Query(1, ge=1),
    per_page: int = Query(10, ge=1, le=100),
    year: int | None = Query(None),
    min_rating: float | None = Query(None, ge=0, le=10),
    max_rating: float | None = Query(None, ge=0, le=10),
    min_price: float | None = Query(None, ge=0),
    max_price: float | None = Query(None, ge=0),
    sort_by: str | None = Query(None),
    order: str = Query("asc"),
    search: str | None = Query(None),
    star: str | None = Query(None),
    director: str | None = Query(None),
    db: AsyncSession = Depends(get_db),
):
    query = select(Movie)

    if search:
        query = query.where(Movie.name.ilike(f"%{search}%"))

    if star:
        query = (
            query
            .join(movie_stars, movie_stars.c.movie_id == Movie.id)
            .join(Star, Star.id == movie_stars.c.star_id)
            .where(Star.name.ilike(f"%{star}%"))
        )

    if director:
        query = (
            query
            .join(
                movie_directors,
                movie_directors.c.movie_id == Movie.id,
            )
            .join(
                Director,
                Director.id == movie_directors.c.director_id,
            )
            .where(Director.name.ilike(f"%{director}%"))
        )

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

    sort_columns = {
        "year": Movie.year,
        "imdb": Movie.imdb,
        "price": Movie.price,
    }

    if sort_by in sort_columns:
        column = sort_columns[sort_by]

        if order == "desc":
            query = query.order_by(desc(column))
        else:
            query = query.order_by(asc(column))

    offset = (page - 1) * per_page

    query = query.offset(offset).limit(per_page)

    result = await db.execute(query)

    movies = result.scalars().unique().all()

    return movies
