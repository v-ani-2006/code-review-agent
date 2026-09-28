"""Entry point shim to support running 'uvicorn main:app --reload' alongside 'uvicorn app.main:app --reload'."""

from app.main import app

__all__ = ["app"]
