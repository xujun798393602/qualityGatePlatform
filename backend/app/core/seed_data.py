from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.core.security import get_password_hash

async def seed_database():
    """Initialize database with default data"""
    async with AsyncSessionLocal() as db:
        admin = await db.query(User).filter(User.username == "admin").first()
        if not admin:
            admin_user = User(
                username="admin",
                email="admin@example.com",
                hashed_password=get_password_hash("Admin@1234"),
                is_active=True,
                is_superuser=True,
            )
            db.add(admin_user)
            await db.commit()
            print("Default admin user created")