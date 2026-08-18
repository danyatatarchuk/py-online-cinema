from datetime import datetime, timedelta

from httpx import ASGITransport, AsyncClient
import pytest
import pytest_asyncio
from jose import jwt

from app.core.security import (
    ALGORITHM,
    SECRET_KEY,
    create_access_token,
    create_refresh_token,
)
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

    assert data["access_token"]
    assert data["refresh_token"]
    assert data["token_type"] == "bearer"

    access_payload = jwt.decode(
        data["access_token"],
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    refresh_payload = jwt.decode(
        data["refresh_token"],
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    assert access_payload["sub"] == "1"
    assert access_payload["type"] == "access"

    assert refresh_payload["sub"] == "1"
    assert refresh_payload["type"] == "refresh"


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
        await client.post(
            "/auth/register",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

        async with AsyncSessionLocal() as db:
            user = await db.get(User, 1)
            token = user.activation_token.token

        response = await client.post(
            f"/auth/activate/{token}",
        )

    assert response.status_code == 200
    assert response.json()["message"] == "User account activated successfully"
    assert response.json()["user_id"] == 1

    async with AsyncSessionLocal() as db:
        user = await db.get(User, 1)

    assert user.is_active is True


@pytest.mark.asyncio
async def test_activate_invalid_token(setup_database):
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
            activation_token = user.activation_token
            activation_token.expires_at = datetime.utcnow() - timedelta(hours=1)
            token = activation_token.token
            await db.commit()

        response = await client.post(
            f"/auth/activate/{token}",
        )

    assert response.status_code == 400
    assert response.json()["detail"] == "Activation token has expired"


@pytest.mark.asyncio
async def test_refresh_access_token(setup_database):
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

        login_response = await client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

        refresh_token = login_response.json()["refresh_token"]

        response = await client.post(
            "/auth/refresh",
            json={
                "refresh_token": refresh_token,
            },
        )

    assert response.status_code == 200

    data = response.json()

    assert data["access_token"]
    assert data["token_type"] == "bearer"

    payload = jwt.decode(
        data["access_token"],
        SECRET_KEY,
        algorithms=[ALGORITHM],
    )

    assert payload["sub"] == "1"
    assert payload["type"] == "access"


@pytest.mark.asyncio
async def test_refresh_with_access_token(setup_database):
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

        login_response = await client.post(
            "/auth/login",
            json={
                "email": "test@example.com",
                "password": "password123",
            },
        )

        access_token = login_response.json()["access_token"]

        response = await client.post(
            "/auth/refresh",
            json={
                "refresh_token": access_token,
            },
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid token type"


@pytest.mark.asyncio
async def test_refresh_with_invalid_token(setup_database):
    transport = ASGITransport(app=app)

    async with AsyncClient(
        transport=transport,
        base_url="http://test",
    ) as client:
        response = await client.post(
            "/auth/refresh",
            json={
                "refresh_token": "invalid-token",
            },
        )

    assert response.status_code == 401
    assert response.json()["detail"] == "Invalid or expired token"
