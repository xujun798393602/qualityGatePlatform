from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.user import User
from app.models.role import Role
from app.models.system_config import SystemConfig
from app.core.security import get_password_hash


async def seed_database():
    """Initialize database with default data"""
    async with AsyncSessionLocal() as db:
        # Seed admin user
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
            print("Default admin user created")

        # Seed default roles
        default_roles = [
            {"name": "admin", "description": "系统管理员", "permissions": ["*"]},
            {"name": "developer", "description": "开发人员", "permissions": ["read", "write", "execute"]},
            {"name": "tester", "description": "测试人员", "permissions": ["read", "execute"]},
            {"name": "viewer", "description": "查看者", "permissions": ["read"]},
        ]
        for role_data in default_roles:
            result = await db.execute(select(Role).where(Role.name == role_data["name"]))
            role = result.scalars().first()
            if not role:
                role = Role(**role_data)
                db.add(role)
                print(f"Role '{role_data['name']}' created")

        # Seed system config
        default_configs = [
            {"key": "app_name", "value": "代码质量门禁管理平台", "description": "系统名称"},
            {"key": "app_version", "value": "0.1.0", "description": "系统版本"},
        ]
        for config_data in default_configs:
            result = await db.execute(select(SystemConfig).where(SystemConfig.key == config_data["key"]))
            config = result.scalars().first()
            if not config:
                config = SystemConfig(**config_data)
                db.add(config)

        await db.commit()
        print("Database initialization completed")
