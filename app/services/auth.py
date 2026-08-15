from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.user import User
from app.schemas.auth import RegisterRequest
from pwdlib import PasswordHash

password_hash = PasswordHash.recommended()


def verify_password(password: str, hashed_password: str) -> bool:
    return password_hash.verify(password, hashed_password)


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
    await db.commit()
    await db.refresh(user)

    return user
