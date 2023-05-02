"""First commit

Revision ID: 82d0384e679f
Revises:
Create Date: 2023-05-02 05:59:22.109496+00:00

"""
import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "82d0384e679f"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tool",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("model_identifier", sa.String(), nullable=True),
        sa.Column("description_", sa.String(), nullable=True),
        sa.Column("ref_name_", sa.String(), nullable=True),
        sa.Column("max_uses_per_query", sa.Integer(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )


def downgrade() -> None:
    op.drop_table("tool")
