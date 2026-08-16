from datetime import datetime, timedelta
from uuid import uuid4

from pwdlib import PasswordHash
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.activation_token import ActivationToken
from app.models.user import User
from app.schemas.auth import RegisterRequest


password_hash = PasswordHash.recommended()


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


async def authenticate_user(
    email: str,
    password: str,
    db: AsyncSession,
) -> User | None:
    result = await db.execute(
        select(User).where(User.email == email)
    )
    user = result.scalar_one_or_none()

    if user is None:
        return None

    if not verify_password(password, user.hashed_password):
        return None

    return user


async def register_user(
    data: RegisterRequest,
    db: AsyncSession,
    group_id: int,
) -> User:
    result = await db.execute(
        select(User).where(User.email == data.email)
    )
    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise ValueError("User with this email already exists")

    user = User(
        email=data.email,
        hashed_password=password_hash.hash(data.password),
        is_active=False,
        group_id=group_id,
    )

    db.add(user)
    await db.flush()

    activation_token = ActivationToken(
        user_id=user.id,
        token=str(uuid4()),
        expires_at=datetime.utcnow() + timedelta(hours=24),
    )

    db.add(activation_token)

    await db.commit()
    await db.refresh(user)

    return user


async def activate_user(
    token: str,
    db: AsyncSession,
) -> User:
    result = await db.execute(
        select(ActivationToken).where(
            ActivationToken.token == token
        )
    )
    activation_token = result.scalar_one_or_none()

    if activation_token is None:
        raise ValueError("Invalid activation token")

    if activation_token.expires_at < datetime.utcnow():
        await db.delete(activation_token)
        await db.commit()
        raise ValueError("Activation token has expired")

    result = await db.execute(
        select(User).where(
            User.id == activation_token.user_id
        )
    )
    user = result.scalar_one_or_none()

    if user is None:
        raise ValueError("User not found")

    user.is_active = True

    await db.delete(activation_token)
    await db.commit()
    await db.refresh(user)

    return user
