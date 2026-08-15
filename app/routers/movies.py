from fastapi import APIRouter, Depends
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
    description="Returns a paginated list of movies.",
)
async def get_movies(
    page: int = 1,
    per_page: int = 10,
    db: AsyncSession = Depends(get_db),
):
    offset = (page - 1) * per_page

    result = await db.execute(
        select(Movie)
        .offset(offset)
        .limit(per_page)
    )

    movies = result.scalars().all()

    return movies
