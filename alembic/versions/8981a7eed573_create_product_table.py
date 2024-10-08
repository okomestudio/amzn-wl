"""Create product table.

Revision ID: 8981a7eed573
Revises:
Create Date: 2023-07-20 17:53:03.037696

"""

import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

from alembic import op

revision = "8981a7eed573"
down_revision = "84f432fe9071"
branch_labels = None
depends_on = None


sql_create_trigger = """
CREATE TRIGGER IF NOT EXISTS
    product_update_updated
AFTER UPDATE ON product
BEGIN
    UPDATE product
    SET updated = DATETIME('now')
    WHERE asin = NEW.asin;
END;
"""

sql_drop_trigger = """
DROP TRIGGER IF EXISTS product_update_updated;
"""


def upgrade() -> None:
    op.create_table(
        "product",
        sa.Column("asin", sqlite.VARCHAR(10), primary_key=True),
        sa.Column(
            "created",
            sqlite.TIMESTAMP,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column(
            "updated",
            sqlite.TIMESTAMP,
            nullable=False,
            server_default=sa.text("CURRENT_TIMESTAMP"),
        ),
        sa.Column("deleted", sqlite.TIMESTAMP, nullable=True),
        sa.Column("title", sqlite.TEXT, nullable=False),
        sa.Column("byline", sqlite.TEXT, nullable=False),
    )
    op.execute(sql_create_trigger)


def downgrade() -> None:
    op.execute(sql_drop_trigger)
    op.drop_table("product")
