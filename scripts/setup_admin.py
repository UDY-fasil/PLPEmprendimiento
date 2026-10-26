"""Setup script: creates base roles and an admin user."""
import os
import sys
import asyncio

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy import select
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker

from app.core.config import settings
from app.core.security import hash_password
from app.modules.auth.models import User, UserStatus, Role, UserRole
from common import resolve_db_url

ADMIN_EMAIL = os.getenv("ADMIN_EMAIL", "admin@plpe.com")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin1234")
ADMIN_NAME = os.getenv("ADMIN_NAME", "Administrador PLPE")

engine = create_async_engine(resolve_db_url(), echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

DEFAULT_ROLES = [
    ("admin", "Acceso total a la plataforma"),
    ("producer", "Productor o emprendedor"),
    ("user", "Usuario consumidor"),
]


async def get_or_create_role(session: AsyncSession, name: str, description: str) -> Role:
    result = await session.execute(select(Role).where(Role.name == name))
    role = result.scalar_one_or_none()
    if role:
        return role
    role = Role(name=name, description=description)
    session.add(role)
    await session.flush()
    print(f"  ✓ Rol '{name}' creado")
    return role


async def main():
    print("🔧 Configurando roles y usuario administrador...")
    async with AsyncSessionLocal() as session:
        roles = {}
        for name, desc in DEFAULT_ROLES:
            roles[name] = await get_or_create_role(session, name, desc)

        result = await session.execute(select(User).where(User.email == ADMIN_EMAIL))
        admin = result.scalar_one_or_none()

        if admin:
            print(f"  · Usuario '{ADMIN_EMAIL}' ya existe (id={admin.id})")
        else:
            admin = User(
                email=ADMIN_EMAIL,
                hashed_password=hash_password(ADMIN_PASSWORD),
                full_name=ADMIN_NAME,
                status=UserStatus.ACTIVE,
                is_verified=True,
            )
            session.add(admin)
            await session.flush()
            print(f"  ✓ Usuario admin creado (id={admin.id})")

        result = await session.execute(
            select(UserRole).where(
                UserRole.user_id == admin.id,
                UserRole.role_id == roles["admin"].id,
            )
        )
        if not result.scalar_one_or_none():
            session.add(UserRole(user_id=admin.id, role_id=roles["admin"].id))
            print("  ✓ Rol 'admin' asignado")

        await session.commit()

    print("\n✅ Listo!")
    print(f"   Email:    {ADMIN_EMAIL}")
    print(f"   Password: {ADMIN_PASSWORD}")


if __name__ == "__main__":
    asyncio.run(main())
