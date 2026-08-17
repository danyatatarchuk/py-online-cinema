import pytest
import pytest_asyncio
from httpx import ASGITransport, AsyncClient

from app.database import Base, AsyncSessionLocal, engine
from app.main import app
from app.models.certification import Certification
from app.models.movie import Movie
from app.models.user import User
from app.models.user_group import UserGroup
from app.services.auth import password_hash


@pytest_asyncio.fixture
async def setup_cart_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        group = UserGroup(name="user")
        db.add(group)
        await db.flush()

        user = User(
            email="cart@example.com",
            hashed_password=password_hash.hash("password123"),
            is_active=True,
            group_id=group.id,
        )
        db.add(user)

        certification = Certification(name="PG-13")
        db.add(certification)
        await db.flush()

        movie = Movie(
            name="Test Movie",
            year=2026,
            time=120,
            imdb=8.0,
            votes=1000,
            meta_score=75.0,
            gross=None,
            description="Test movie for cart.",
            price=9.99,
            certification_id=certification.id,
        )
        db.add(movie)

        await db.commit()

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


async def get_access_token(client: AsyncClient) -> str:
    response = await client.post(
        "/auth/login",
        json={
            "email": "cart@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_add_movie_to_cart(setup_cart_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        token = await get_access_token(client)

        response = await client.post(
            "/cart/items/1",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["movie_id"] == 1
    assert data["movie_name"] == "Test Movie"
    assert data["price"] == "9.99"


@pytest.mark.asyncio
async def test_add_movie_to_cart_duplicate(setup_cart_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        token = await get_access_token(client)

        first_response = await client.post(
            "/cart/items/1",
            headers={"Authorization": f"Bearer {token}"},
        )

        second_response = await client.post(
            "/cart/items/1",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert first_response.status_code == 201
    assert second_response.status_code == 400
    assert second_response.json()["detail"] == "Movie is already in cart"


@pytest.mark.asyncio
async def test_remove_movie_from_cart(setup_cart_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        token = await get_access_token(client)

        add_response = await client.post(
            "/cart/items/1",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert add_response.status_code == 201

        response = await client.delete(
            "/cart/items/1",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 204


@pytest.mark.asyncio
async def test_view_cart(setup_cart_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        token = await get_access_token(client)

        await client.post(
            "/cart/items/1",
            headers={"Authorization": f"Bearer {token}"},
        )

        response = await client.get(
            "/cart",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200

    data = response.json()

    assert len(data["items"]) == 1
    assert data["items"][0]["movie_id"] == 1
    assert data["items"][0]["movie_name"] == "Test Movie"
    assert data["items"][0]["price"] == "9.99"


@pytest.mark.asyncio
async def test_cart_requires_authentication(setup_cart_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get("/cart")

    assert response.status_code == 401
