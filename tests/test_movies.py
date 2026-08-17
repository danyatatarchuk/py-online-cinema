import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.database import Base, AsyncSessionLocal, engine
from app.main import app
from app.models.certification import Certification
from app.models.movie import Movie


@pytest_asyncio.fixture
async def setup_movies_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        certification = Certification(name="PG-13")

        db.add(certification)
        await db.flush()

        movies = [
            Movie(
                name="Movie One",
                year=2020,
                time=120,
                imdb=8.5,
                votes=1000,
                meta_score=80.0,
                gross=100.0,
                description="First test movie",
                price=9.99,
                certification_id=certification.id,
            ),
            Movie(
                name="Movie Two",
                year=2021,
                time=110,
                imdb=7.5,
                votes=800,
                meta_score=70.0,
                gross=80.0,
                description="Second test movie",
                price=7.99,
                certification_id=certification.id,
            ),
            Movie(
                name="Movie Three",
                year=2022,
                time=130,
                imdb=9.0,
                votes=1500,
                meta_score=90.0,
                gross=120.0,
                description="Third test movie",
                price=12.99,
                certification_id=certification.id,
            ),
        ]

        db.add_all(movies)
        await db.commit()

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_get_movies(setup_movies_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get("/movies")

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 3
    assert data[0]["name"] == "Movie One"
    assert data[1]["name"] == "Movie Two"
    assert data[2]["name"] == "Movie Three"


@pytest.mark.asyncio
async def test_get_movies_pagination(setup_movies_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/movies",
            params={
                "page": 1,
                "per_page": 2,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Movie One"
    assert data[1]["name"] == "Movie Two"


@pytest.mark.asyncio
async def test_get_movies_second_page(setup_movies_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/movies",
            params={
                "page": 2,
                "per_page": 2,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Movie Three"


@pytest.mark.asyncio
async def test_get_movies_empty_page(setup_movies_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/movies",
            params={
                "page": 10,
                "per_page": 10,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data == []


@pytest.mark.asyncio
async def test_filter_movies_by_year(setup_movies_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/movies",
            params={"year": 2021},
        )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Movie Two"


@pytest.mark.asyncio
async def test_filter_movies_by_rating(setup_movies_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/movies",
            params={
                "min_rating": 8,
                "max_rating": 9,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 2
    assert data[0]["name"] == "Movie One"
    assert data[1]["name"] == "Movie Three"


@pytest.mark.asyncio
async def test_filter_movies_by_price(setup_movies_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/movies",
            params={
                "min_price": 8,
                "max_price": 10,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["name"] == "Movie One"


@pytest.mark.asyncio
async def test_sort_movies_by_year_desc(setup_movies_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/movies",
            params={
                "sort_by": "year",
                "order": "desc",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert [movie["name"] for movie in data] == [
        "Movie Three",
        "Movie Two",
        "Movie One",
    ]


@pytest.mark.asyncio
async def test_sort_movies_by_rating_desc(setup_movies_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/movies",
            params={
                "sort_by": "imdb",
                "order": "desc",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert [movie["name"] for movie in data] == [
        "Movie Three",
        "Movie One",
        "Movie Two",
    ]


@pytest.mark.asyncio
async def test_sort_movies_by_price_asc(setup_movies_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get(
            "/movies",
            params={
                "sort_by": "price",
                "order": "asc",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert [movie["name"] for movie in data] == [
        "Movie Two",
        "Movie One",
        "Movie Three",
    ]
