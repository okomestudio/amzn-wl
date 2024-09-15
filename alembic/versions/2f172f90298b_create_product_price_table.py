"""Create product_price table.

Revision ID: 2f172f90298b
Revises: 8981a7eed573
Create Date: 2023-07-20 18:56:24.997189

"""

import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

from alembic import op

revision = "2f172f90298b"
down_revision = "8981a7eed573"
branch_labels = None
depends_on = None


sql_create_trigger = """
CREATE TRIGGER IF NOT EXISTS
    product_price_update_updated
AFTER UPDATE ON product_price
BEGIN
    UPDATE product_price
    SET updated = DATETIME('now')
    WHERE product_price_id = NEW.product_price_id;
END;
"""

sql_drop_trigger = """
DROP TRIGGER IF EXISTS product_price_update_updated;
"""


def upgrade() -> None:
    op.create_table(
        "product_price",
        sa.Column(
            "product_price_id", sqlite.INTEGER, primary_key=True, autoincrement="auto"
        ),
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
        sa.Column("asin", sqlite.VARCHAR(10), sa.ForeignKey("product.asin")),
        sa.Column("hostname", sqlite.TEXT, sa.ForeignKey("site.hostname")),
        sa.Column("value", sqlite.DECIMAL, nullable=False),
        sa.Column("currency", sqlite.VARCHAR(1), nullable=False),
    )
    op.execute(sql_create_trigger)


def downgrade() -> None:
    op.execute(sql_drop_trigger)
    op.drop_table("product_price")
