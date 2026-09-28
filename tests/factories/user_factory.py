"""User model factory producing realistic user accounts for testing."""
import uuid
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.security import get_password_hash
from app.models.user import User

fake = Faker()


class UserFactory:
    """Factory generating User entity instances."""

    @classmethod
    def build(
        cls,
        id: uuid.UUID = None,
        username: str = None,
        email: str = None,
        password: str = "TestPass123!",
        full_name: str = None,
        is_active: bool = True,
        is_admin: bool = False,
    ) -> User:
        """Construct User instance without database persistence."""
        user_id = id or uuid.uuid4()
        uname = username or f"{fake.user_name()}_{str(user_id)[:6]}"
        mail = email or f"{uname}@{fake.free_email_domain()}"
        return User(
            id=user_id,
            username=uname,
            email=mail,
            password_hash=get_password_hash(password),
            full_name=full_name or fake.name(),
            is_active=is_active,
            is_admin=is_admin,
        )

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs) -> User:
        """Construct and persist User entity in database session."""
        user = cls.build(**kwargs)
        db.add(user)
        await db.flush()
        await db.refresh(user)
        return user
