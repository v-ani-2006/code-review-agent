import uuid
from typing import Optional
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import hash_password
from app.models.user import User
from app.repositories.base_repository import BaseRepository


class UserRepository(BaseRepository[User]):
    """Repository handling database operations for User entities."""

    def __init__(self):
        super().__init__(User)

    async def get_by_email(self, db: AsyncSession, email: str) -> Optional[User]:
        """Lookup a user by exact email address."""
        statement = select(User).where(User.email == email.lower().strip())
        result = await db.execute(statement)
        return result.scalars().first()

    async def get_by_username(self, db: AsyncSession, username: str) -> Optional[User]:
        """Lookup a user by exact username."""
        statement = select(User).where(User.username == username.strip())
        result = await db.execute(statement)
        return result.scalars().first()

    async def create_user(
        self,
        db: AsyncSession,
        username: str,
        email: str,
        password: str,
        full_name: Optional[str] = None,
        is_admin: bool = False,
    ) -> User:
        """Hash password, create, and persist a new user record."""
        hashed_password = hash_password(password)
        return await self.create(
            db,
            username=username.strip(),
            email=email.lower().strip(),
            password_hash=hashed_password,
            full_name=full_name,
            is_active=True,
            is_admin=is_admin,
        )

    async def activate_user(
        self,
        db: AsyncSession,
        user_id: uuid.UUID,
        is_active: bool = True,
    ) -> Optional[User]:
        """Toggle active status for a user."""
        user = await self.get_by_id(db, user_id)
        if not user:
            return None
        user.is_active = is_active
        await db.commit()
        await db.refresh(user)
        return user


# Singleton repository instance
user_repository = UserRepository()
