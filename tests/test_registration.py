from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio

from app.database import Base, AsyncSessionLocal, engine
from app.main import app
from app.models.user import User
from app.models.user_group import UserGroup
from app.services.auth import password_hash


@pytest_asyncio.fixture
async def setup_database():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)

    async with AsyncSessionLocal() as db:
        db.add(UserGroup(name="user"))
        await db.commit()

    yield

    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest.mark.asyncio
async def test_register_user(setup_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

    assert response.status_code == 201

    data = response.json()

    assert data["email"] == "test@example.com"
    assert data["is_active"] is False
    assert data["id"] == 1


@pytest.mark.asyncio
async def test_register_invalid_email(setup_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/auth/register",
            json={
                "email": "invalid-email",
                "password": "password123",
            },
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_short_password(setup_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "short",
            },
        )

    assert response.status_code == 422


@pytest.mark.asyncio
async def test_register_duplicate_email(setup_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        first_response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

        second_response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password456",
            },
        )

    assert first_response.status_code == 201
    assert second_response.status_code == 400


@pytest.mark.asyncio
async def test_password_is_hashed(setup_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

    assert response.status_code == 201

    async with AsyncSessionLocal() as db:
        user = await db.get(User, 1)

    assert user.hashed_password != "password123"
    assert password_hash.verify(
        "password123",
        user.hashed_password,
    )


@pytest.mark.asyncio
async def test_login_user(setup_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

        async with AsyncSessionLocal() as db:
            user = await db.get(User, 1)
            user.is_active = True
            await db.commit()

        response = await client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["id"] == 1
    assert data["email"] == "test@example.com"
    assert data["is_active"] is True


@pytest.mark.asyncio
async def test_login_invalid_password(setup_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

        async with AsyncSessionLocal() as db:
            user = await db.get(User, 1)
            user.is_active = True
            await db.commit()

        response = await client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "wrongpassword",
            },
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_login_nonexistent_user(setup_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/auth/login",
            json={
                "email": "unknown@example.com",
                "password": "password123",
            },
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid email or password"


@pytest.mark.asyncio
async def test_login_inactive_user(setup_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

        response = await client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

    assert response.status_code == 403
    assert response.json()["detail"] == "User account is inactive"


@pytest.mark.asyncio
async def test_activate_user(setup_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

        assert response.status_code == 201

        async with AsyncSessionLocal() as db:
            user = await db.get(User, 1)
            token = user.activation_token.token

        response = await client.post(
            f"/auth/activate/{token}",
        )

    assert response.status_code == 200

    data = response.json()

    assert data["message"] == "User account activated successfully"
    assert data["user_id"] == 1

    async with AsyncSessionLocal() as db:
        user = await db.get(User, 1)

    assert user.is_active is True
    assert user.activation_token is None


@pytest.mark.asyncio
async def test_activate_user_invalid_token(setup_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/auth/activate/invalid-token",
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Invalid activation token"


@pytest.mark.asyncio
async def test_activate_user_expired_token(setup_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

        async with AsyncSessionLocal() as db:
            user = await db.get(User, 1)
            user.activation_token.expires_at = (
                user.activation_token.expires_at.replace(year=2020)
            )
            token = user.activation_token.token
            await db.commit()

        response = await client.post(
            f"/auth/activate/{token}",
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Activation token has expired"

    async with AsyncSessionLocal() as db:
        user = await db.get(User, 1)

    assert user.is_active is False
    assert user.activation_token is None
