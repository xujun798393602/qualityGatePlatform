from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash


async def seed_database():
    """Initialize database with default data"""
    async with AsyncSessionLocal() as db:
        result = await db.execute(select(User).where(User.username == "admin"))
        admin = result.scalars().first()
        if not admin:
            admin_user = User(
                username="admin",
                password_hash=get_password_hash("Admin@1234"),
                name="Administrator",
                email="admin@example.com",
                is_active=True,
            )
            db.add(admin_user)
            await db.commit()
            print("Default admin user created")
