"""Create product table.

Revision ID: 8981a7eed573
Revises:
Create Date: 2023-07-20 17:53:03.037696

"""
import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "8981a7eed573"
down_revision = None
branch_labels = None
depends_on = None


sql_create_trigger = """
CREATE TRIGGER IF NOT EXISTS
    product_update_updated
AFTER UPDATE ON product
BEGIN
    UPDATE product
    SET updated = DATETIME('NOW')
    WHERE product_id = NEW.product_id;
END;
"""

sql_drop_trigger = """
DROP TRIGGER IF EXISTS product_update_updated;
"""


def upgrade() -> None:  # noqa
    op.create_table(
        "product",
        sa.Column("product_id", sa.String(), primary_key=True),
        sa.Column(
            "created",
            sa.TIMESTAMP,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated",
            sa.TIMESTAMP,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("deleted", sa.TIMESTAMP, nullable=True),
        sa.Column("title", sa.String(), nullable=False),
        sa.Column("byline", sa.String(), nullable=False),
    )
    op.execute(sql_create_trigger)


def downgrade() -> None:  # noqa
    op.execute(sql_drop_trigger)
    op.drop_table("product")
