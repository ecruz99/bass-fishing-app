"""enable pgvector extension

Revision ID: 3b4abe6bfe00
Revises:
Create Date: 2026-10-05 01:27:44.571826

"""

from collections.abc import Sequence

from alembic import op

# revision identifiers, used by Alembic.
revision: str = "3b4abe6bfe00"
down_revision: str | Sequence[str] | None = None
branch_labels: str | Sequence[str] | None = None
depends_on: str | Sequence[str] | None = None


def upgrade() -> None:
    """Enable pgvector, which stores and searches the knowledge base embeddings."""
    op.execute("CREATE EXTENSION IF NOT EXISTS vector")


def downgrade() -> None:
    """Disable pgvector. Fails if any table still uses the vector type."""
    op.execute("DROP EXTENSION IF EXISTS vector")
