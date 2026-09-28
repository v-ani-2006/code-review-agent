from typing import Any, Dict, Generic, List, Optional, Type, TypeVar
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from app.models.base import Base

ModelType = TypeVar("ModelType", bound=Base)


class BaseRepository(Generic[ModelType]):
    """Generic repository providing asynchronous CRUD operations for SQLAlchemy models."""

    def __init__(self, model: Type[ModelType]):
        self.model = model

    async def get_by_id(self, db: AsyncSession, id: Any) -> Optional[ModelType]:
        """Fetch a single record by primary key."""
        result = await db.get(self.model, id)
        return result

    async def get_all(
        self,
        db: AsyncSession,
        skip: int = 0,
        limit: int = 100,
    ) -> List[ModelType]:
        """Fetch multiple records with pagination."""
        statement = select(self.model).offset(skip).limit(limit)
        result = await db.execute(statement)
        return list(result.scalars().all())

    async def create(self, db: AsyncSession, **attributes: Any) -> ModelType:
        """Instantiate, persist, and refresh a new database record."""
        instance = self.model(**attributes)
        db.add(instance)
        await db.commit()
        await db.refresh(instance)
        return instance

    async def update(
        self,
        db: AsyncSession,
        db_obj: ModelType,
        update_data: Dict[str, Any],
    ) -> ModelType:
        """Update existing record attributes, commit, and refresh."""
        for field, value in update_data.items():
            if hasattr(db_obj, field):
                setattr(db_obj, field, value)
        await db.commit()
        await db.refresh(db_obj)
        return db_obj

    async def delete(self, db: AsyncSession, id: Any) -> bool:
        """Delete a record by primary key. Returns True if deleted, False if not found."""
        instance = await self.get_by_id(db, id)
        if not instance:
            return False
        await db.delete(instance)
        await db.commit()
        return True

    async def exists(self, db: AsyncSession, id: Any) -> bool:
        """Check if a record with the given primary key exists."""
        instance = await self.get_by_id(db, id)
        return instance is not None
