"""add ai fields to reviews

Revision ID: 002_add_ai_fields
Revises: 001_initial_schema
Create Date: 2026-09-27 23:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '002_add_ai_fields'
down_revision: Union[str, None] = '001_initial_schema'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS ai_summary TEXT")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS ai_strengths TEXT")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS ai_recommendations TEXT")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS ai_bugfix TEXT")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS ai_documentation TEXT")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS ai_test_code TEXT")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS ai_model VARCHAR(100)")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS ai_processing_time DOUBLE PRECISION")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS ai_created_at TIMESTAMP WITH TIME ZONE")


def downgrade() -> None:
    op.drop_column('reviews', 'ai_created_at')
    op.drop_column('reviews', 'ai_processing_time')
    op.drop_column('reviews', 'ai_model')
    op.drop_column('reviews', 'ai_test_code')
    op.drop_column('reviews', 'ai_documentation')
    op.drop_column('reviews', 'ai_bugfix')
    op.drop_column('reviews', 'ai_recommendations')
    op.drop_column('reviews', 'ai_strengths')
    op.drop_column('reviews', 'ai_summary')
