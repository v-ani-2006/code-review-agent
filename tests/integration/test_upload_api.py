"""Integration tests for file upload, batch upload, and archive endpoints."""
import io
import httpx
import pytest

from app.models.user import User
from tests.sample_files import PROJECT_SAMPLE_ZIP_PATH


@pytest.mark.integration
async def test_api_upload_single_file(authenticated_client: httpx.AsyncClient, test_user: User):
    """Test POST /upload/file uploads and reviews a python script."""
    code_content = b"def calculate():\n    return 100\n"
    files = {"file": ("calculator.py", io.BytesIO(code_content), "text/x-python")}

    response = await authenticated_client.post("/upload/file", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["upload"]["original_filename"] == "calculator.py"
    assert data["review"]["overall_score"] > 0


@pytest.mark.integration
async def test_api_upload_invalid_extension(authenticated_client: httpx.AsyncClient):
    """Test POST /upload/file rejects disallowed file extensions."""
    files = {"file": ("script.exe", io.BytesIO(b"binary"), "application/octet-stream")}
    response = await authenticated_client.post("/upload/file", files=files)
    assert response.status_code == 400


@pytest.mark.integration
async def test_api_upload_multiple(authenticated_client: httpx.AsyncClient, test_user: User):
    """Test POST /upload/multiple uploads multiple files simultaneously."""
    files = [
        ("files", ("mod_a.py", io.BytesIO(b"x = 1\n"), "text/x-python")),
        ("files", ("mod_b.py", io.BytesIO(b"y = 2\n"), "text/x-python")),
    ]
    response = await authenticated_client.post("/upload/multiple", files=files)
    assert response.status_code == 201
    data = response.json()
    assert data["total_files"] == 2


@pytest.mark.integration
async def test_api_upload_zip(authenticated_client: httpx.AsyncClient, test_user: User):
    """Test POST /upload/zip uploads and queues an archive for processing."""
    zip_bytes = PROJECT_SAMPLE_ZIP_PATH.read_bytes()
    files = {"file": ("project.zip", io.BytesIO(zip_bytes), "application/zip")}

    response = await authenticated_client.post("/upload/zip", files=files)
    assert response.status_code == 202
    data = response.json()
    assert "task_id" in data


@pytest.mark.integration
async def test_api_get_user_uploads(authenticated_client: httpx.AsyncClient, test_user: User):
    """Test GET /upload/user lists user uploaded assets."""
    response = await authenticated_client.get("/upload/user")
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, list)
