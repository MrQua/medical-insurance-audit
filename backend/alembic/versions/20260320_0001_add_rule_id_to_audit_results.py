"""add rule_id to audit_results

Revision ID: 20260320_0001
Revises:
Create Date: 2026-03-20 00:00:00
"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "20260320_0001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TABLE IF EXISTS audit_results ADD COLUMN IF NOT EXISTS rule_id VARCHAR(36)")


def downgrade() -> None:
    op.execute("ALTER TABLE IF EXISTS audit_results DROP COLUMN IF EXISTS rule_id")
