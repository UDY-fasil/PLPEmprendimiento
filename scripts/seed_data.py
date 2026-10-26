"""Seed script to populate PLPE database with fictional data."""
import os
import sys

# Add project root to path
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy import text
from sqlalchemy.orm import sessionmaker
import asyncio
import random
from datetime import datetime, timedelta

from app.modules.business.models.product import Product as ProductModel
from app.modules.business.models.business import BusinessStatus
from common import resolve_db_url

engine = create_async_engine(resolve_db_url(), echo=False)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)


async def clear_tables():
    """Clear all data in correct order due to foreign key constraints."""
    async with AsyncSessionLocal() as session:
        await session.execute(text("SET FOREIGN_KEY_CHECKS=0"))
        await session.execute(text("DELETE FROM products"))
        await session.execute(text("DELETE FROM favorites"))
        await session.execute(text("DELETE FROM inquiries"))
        await session.execute(text("DELETE FROM services"))
        await session.execute(text("DELETE FROM businesses"))
        await session.execute(text("DELETE FROM categories"))
        await session.execute(text("DELETE FROM users"))
        await session.execute(text("SET FOREIGN_KEY_CHECKS=1"))
        await session.commit()
        print("✓ Tables cleared")


async def seed_users(n=8):
    """Seed fictional users."""
    async with AsyncSessionLocal() as session:
        for i in range(1, n + 1):
            email = f"productor{i}@test.com"
            full_name = f"Productor {i}"
            phone = f"+549114{i:07d}"[-7:]
            city = random.choice(["Buenos Aires", "Córdoba", "Rosario", "Mar del Plata", "Mendoza"])

            await session.execute(
                text(
                    """INSERT INTO users (email, hashed_password, full_name, phone, city, status, is_verified, totp_enabled, failed_login_attempts, created_at) 
                       VALUES (:email, :password, :full_name, :phone, :city, 'active', true, false, 0, :created_at)"""
                ),
                {
                    "email": email,
                    "password": "password123",
                    "full_name": full_name,
                    "phone": phone,
                    "city": city,
                    "created_at": datetime.utcnow(),
                },
            )
        await session.commit()
        print(f"✓ Inserted {n} users")


async def seed_categories(n=6):
    """Seed fictional categories."""
    categories = [
        "Alimentos y Bebidas",
        "Artesanía",
        "Ropa y Accesorios",
        "Tecnología y Software",
        "Salud y Bienestar",
        "Decoración y Hogar",
        "Servicios Profesionales",
        "Deporte y Aventura",
    ]

    async with AsyncSessionLocal() as session:
        for i, name in enumerate(categories[:n], 1):
            await session.execute(
                text(
                    """INSERT INTO categories (name, description, active) 
                       VALUES (:name, :description, true)"""
                ),
                {"name": name, "description": f"Categoría de productos {name.lower()}"},
            )
        await session.commit()
        print(f"✓ Inserted {n} categories")


async def seed_businesses(n=12):
    """Seed fictional businesses."""
    status_choices = [s.value for s in BusinessStatus]

    async with AsyncSessionLocal() as session:
        # Get existing users as potential owners
        result = await session.execute(text("SELECT id FROM users ORDER BY RAND() LIMIT 10"))
        users = [row[0] for row in result.fetchall()]

        for i in range(1, n + 1):
            owner = random.choice(users) if users else i
            name = f"Emprendimiento {i}"
            description = f"Descripción del emprendimiento {i} - productos artesanales y locales"
            city = random.choice(["Buenos Aires", "Córdoba", "Rosario", "Mar del Plata", "Mendoza"])
            status = random.choice(status_choices)

            await session.execute(
                text(
                    """INSERT INTO businesses (owner_id, name, description, city, status, created_at) 
                       VALUES (:owner_id, :name, :description, :city, :status, :created_at)"""
                ),
                {
                    "owner_id": owner,
                    "name": name,
                    "description": description,
                    "city": city,
                    "status": status,
                    "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 90)),
                },
            )
        await session.commit()
        print(f"✓ Inserted {n} businesses")


async def seed_products(n=25):
    """Seed fictional products."""
    async with AsyncSessionLocal() as session:
        # Get business IDs
        result = await session.execute(text("SELECT id FROM businesses ORDER BY RAND() LIMIT 20"))
        businesses = [row[0] for row in result.fetchall()]

        for i in range(1, n + 1):
            business = random.choice(businesses) if businesses else 1
            name = f"Producto {i}"
            description = f"Descripción del producto {i}"
            price = round(random.uniform(100, 5000), 2)
            currency = "ARS"
            stock = random.randint(1, 500)
            image_url = f"https://via.placeholder.com/300x200?product={i}"
            active = random.choice([True, True, True, False])

            await session.execute(
                text(
                    """INSERT INTO products (business_id, name, description, price, currency, stock, image_url, active, created_at) 
                       VALUES (:business_id, :name, :description, :price, :currency, :stock, :image_url, :active, :created_at)"""
                ),
                {
                    "business_id": business,
                    "name": name,
                    "description": description,
                    "price": price,
                    "currency": currency,
                    "stock": stock,
                    "image_url": image_url,
                    "active": active,
                    "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 60)),
                },
            )
        await session.commit()
        print(f"✓ Inserted {n} products")


async def seed_favorites(n=15):
    """Seed fictional favorites."""
    async with AsyncSessionLocal() as session:
        # Get user and business IDs
        result = await session.execute(text("SELECT id FROM users ORDER BY RAND() LIMIT 10"))
        users = [row[0] for row in result.fetchall()]

        result = await session.execute(text("SELECT id FROM businesses ORDER BY RAND() LIMIT 15"))
        businesses = [row[0] for row in result.fetchall()]

        for i in range(1, n + 1):
            user = random.choice(users) if users else 1
            business = random.choice(businesses) if businesses else 1

            await session.execute(
                text(
                    """INSERT INTO favorites (user_id, business_id, product_id, created_at) 
                       VALUES (:user_id, :business_id, NULL, :created_at)"""
                ),
                {
                    "user_id": user,
                    "business_id": business,
                    "created_at": datetime.utcnow() - timedelta(days=random.randint(1, 30)),
                },
            )
        await session.commit()
        print(f"✓ Inserted {n} favorites")


async def main():
    print("🌱 Starting to seed fictional data...")
    await clear_tables()
    await seed_users(8)
    await seed_categories(6)
    await seed_businesses(12)
    await seed_products(25)
    await seed_favorites(15)
    print("\n✅ All fictional data seeded successfully!")


if __name__ == "__main__":
    asyncio.run(main())