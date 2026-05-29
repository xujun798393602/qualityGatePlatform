from sqlalchemy.ext.asyncio import AsyncSession
from app.models.user import User
from app.core.security import verify_password, get_password_hash

class AuthService:
    @staticmethod
    async def authenticate_user(db: AsyncSession, username: str, password: str):
        user = await db.query(User).filter(User.username == username).first()
        if not user:
            return None
        if not verify_password(password, user.hashed_password):
            return None
        return user

    @staticmethod
    async def create_user(db: AsyncSession, username: str, email: str, password: str):
        hashed_password = get_password_hash(password)
        user = User(
            username=username,
            email=email,
            hashed_password=hashed_password,
            is_active=True,
        )
        db.add(user)
        await db.commit()
        await db.refresh(user)
        return user