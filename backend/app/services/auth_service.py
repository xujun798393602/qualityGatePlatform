from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import verify_password, get_password_hash


class AuthService:
    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str):
        result = await db.execute(select(User).where(User.username == username))
        user = result.scalars().first()
        if not user:
            return None
        if not verify_password(password, user.password_hash):
            return None
        return user

    @staticmethod
    async def create_user(db: AsyncSession, username: str, email: str, password: str):
        password_hash = get_password_hash(password)
        user = User(
            username=username,
            password_hash=password_hash,
            name=username,
            email=email,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user
