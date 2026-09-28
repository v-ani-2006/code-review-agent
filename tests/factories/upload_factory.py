"""Upload model factory producing realistic upload records for testing."""
import hashlib
import uuid
from faker import Faker
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.upload import Upload

fake = Faker()


class UploadFactory:
    """Factory generating Upload entity instances."""

    @classmethod
    def build(
        cls,
        id: uuid.UUID = None,
        user_id: uuid.UUID = None,
        original_filename: str = None,
        stored_filename: str = None,
        file_size: int = 1024,
        file_hash: str = None,
        mime_type: str = "text/x-python",
        language: str = "python",
        review_id: uuid.UUID = None,
    ) -> Upload:
        upload_id = id or uuid.uuid4()
        fname = original_filename or f"script_{str(upload_id)[:6]}.py"
        return Upload(
            id=upload_id,
            user_id=user_id or uuid.uuid4(),
            original_filename=fname,
            stored_filename=stored_filename or f"{upload_id}_{fname}",
            file_size=file_size,
            file_hash=file_hash or hashlib.sha256(fname.encode("utf-8")).hexdigest(),
            mime_type=mime_type,
            language=language,
            review_id=review_id,
        )

    @classmethod
    async def create(cls, db: AsyncSession, **kwargs) -> Upload:
        upload = cls.build(**kwargs)
        db.add(upload)
        await db.flush()
        await db.refresh(upload)
        return upload
