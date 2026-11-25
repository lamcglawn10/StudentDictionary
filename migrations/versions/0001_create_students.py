"""Create students table.

Revision ID: 0001_create_students
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001_create_students"
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    op.create_table(
        "students",
        sa.Column("id", sa.Integer(), primary_key=True, nullable=False),
        sa.Column("name", sa.String(length=120), nullable=False),
        sa.Column("age", sa.Integer(), nullable=False),
        sa.Column("email", sa.String(length=254), nullable=False),
    )


def downgrade():
    op.drop_table("students")
