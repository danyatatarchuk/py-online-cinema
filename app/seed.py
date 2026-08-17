import asyncio
from decimal import Decimal

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.certification import Certification
from app.models.movie import Movie
from app.models.user_group import UserGroup


async def seed_data():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(UserGroup).where(UserGroup.name == "user")
        )
        group = result.scalar_one_or_none()

        if group is None:
            db.add(UserGroup(name="user"))

        result = await db.execute(
            select(Certification).where(Certification.name == "PG-13")
        )
        certification = result.scalar_one_or_none()

        if certification is None:
            certification = Certification(name="PG-13")
            db.add(certification)
            await db.flush()

        result = await db.execute(
            select(Movie).where(Movie.name == "Test Movie")
        )
        movie = result.scalar_one_or_none()

        if movie is None:
            movie = Movie(
                name="Test Movie",
                year=2026,
                time=120,
                imdb=8.0,
                votes=1000,
                meta_score=80.0,
                gross=1000000.0,
                description="Test movie for cart and order testing.",
                price=Decimal("9.99"),
                certification_id=certification.id,
            )
            db.add(movie)

        await db.commit()

        print("Seed data created successfully.")


if __name__ == "__main__":
    asyncio.run(seed_data())
