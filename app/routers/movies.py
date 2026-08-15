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
    summary="Get all movies",
    description="Returns a list of all movies.",
)
async def get_movies(
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Movie)
    )
    movies = result.scalars().all()

    return movies
