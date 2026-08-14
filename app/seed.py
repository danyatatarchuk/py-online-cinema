import asyncio

from sqlalchemy import select

from app.database import AsyncSessionLocal
from app.models.user_group import UserGroup


async def seed_user_group():
    async with AsyncSessionLocal() as db:
        result = await db.execute(
            select(UserGroup).where(UserGroup.name == "user")
        )
        group = result.scalar_one_or_none()

        if group is None:
            db.add(UserGroup(name="user"))
            await db.commit()
            print("User group created.")
        else:
            print("User group already exists.")


if __name__ == "__main__":
    asyncio.run(seed_user_group())
