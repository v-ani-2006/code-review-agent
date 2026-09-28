"""Upload and task fixtures with temporary directory isolation."""
from pathlib import Path
import pytest
import pytest_asyncio
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import settings
from app.models.task import Task
from app.models.upload import Upload
from app.models.user import User
from tests.factories.task_factory import TaskFactory
from tests.factories.upload_factory import UploadFactory


@pytest.fixture
def isolated_upload_dir(tmp_path: Path) -> Path:
    """Provide a temporary directory for file upload operations."""
    test_upload_dir = tmp_path / "uploads"
    test_upload_dir.mkdir(parents=True, exist_ok=True)
    return test_upload_dir


@pytest_asyncio.fixture(scope="function")
async def sample_upload(db_session: AsyncSession, test_user: User) -> Upload:
    """Create and persist single upload record."""
    return await UploadFactory.create(
        db=db_session,
        user_id=test_user.id,
        original_filename="calculator.py",
        file_size=512,
    )


@pytest_asyncio.fixture(scope="function")
async def sample_task(db_session: AsyncSession, test_user: User) -> Task:
    """Create and persist single background task record."""
    return await TaskFactory.create(
        db=db_session,
        user_id=test_user.id,
        task_type="batch_upload",
        status="COMPLETED",
    )
