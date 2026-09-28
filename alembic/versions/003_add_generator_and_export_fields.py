"""add generator and export fields to reviews

Revision ID: 003_add_generator_and_export_fields
Revises: 002_add_ai_fields
Create Date: 2026-09-28 00:00:00.000000

"""
from typing import Sequence, Union
from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = '003_generator_export_fields'
down_revision: Union[str, None] = '002_add_ai_fields'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS documentation TEXT")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS docstrings TEXT")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS readme_markdown TEXT")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS unit_tests TEXT")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS refactored_code TEXT")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS architecture_summary TEXT")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS changelog TEXT")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS export_markdown TEXT")
    op.execute("ALTER TABLE reviews ADD COLUMN IF NOT EXISTS export_html TEXT")


def downgrade() -> None:
    op.drop_column('reviews', 'export_html')
    op.drop_column('reviews', 'export_markdown')
    op.drop_column('reviews', 'changelog')
    op.drop_column('reviews', 'architecture_summary')
    op.drop_column('reviews', 'refactored_code')
    op.drop_column('reviews', 'unit_tests')
    op.drop_column('reviews', 'readme_markdown')
    op.drop_column('reviews', 'docstrings')
    op.drop_column('reviews', 'documentation')
