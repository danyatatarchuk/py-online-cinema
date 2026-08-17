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
async def setup_order_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        group = UserGroup(name="user")
        db.add(group)
        await db.flush()

        user = User(
            email="order@example.com",
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
            description="Test movie for order.",
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
            "email": "order@example.com",
            "password": "password123",
        },
    )

    assert response.status_code == 200

    return response.json()["access_token"]


@pytest.mark.asyncio
async def test_create_order(setup_order_database):
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

        response = await client.post(
            "/orders",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 201

    data = response.json()

    assert data["id"] == 1
    assert data["status"] == "pending"
    assert data["total_amount"] == "9.99"
    assert len(data["items"]) == 1
    assert data["items"][0]["movie_id"] == 1
    assert data["items"][0]["movie_name"] == "Test Movie"
    assert data["items"][0]["price_at_order"] == "9.99"


@pytest.mark.asyncio
async def test_get_user_orders(setup_order_database):
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

        create_response = await client.post(
            "/orders",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert create_response.status_code == 201

        response = await client.get(
            "/orders",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200

    data = response.json()

    assert len(data) == 1
    assert data[0]["id"] == 1
    assert data[0]["status"] == "pending"
    assert data[0]["total_amount"] == "9.99"
    assert data[0]["items"][0]["movie_name"] == "Test Movie"


@pytest.mark.asyncio
async def test_get_order_details(setup_order_database):
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

        create_response = await client.post(
            "/orders",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert create_response.status_code == 201

        response = await client.get(
            "/orders/1",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["status"] == "pending"
    assert data["total_amount"] == "9.99"
    assert len(data["items"]) == 1
    assert data["items"][0]["movie_id"] == 1
    assert data["items"][0]["movie_name"] == "Test Movie"
    assert data["items"][0]["price_at_order"] == "9.99"


@pytest.mark.asyncio
async def test_get_order_not_found(setup_order_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        token = await get_access_token(client)

        response = await client.get(
            "/orders/999",
            headers={"Authorization": f"Bearer {token}"},
        )

    assert response.status_code == 404
    assert response.json()["detail"] == "Order not found"


@pytest.mark.asyncio
async def test_orders_require_authentication(setup_order_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.get("/orders")

    assert response.status_code == 401
