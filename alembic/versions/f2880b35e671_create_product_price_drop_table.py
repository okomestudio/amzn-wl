"""create product_price_drop table

Revision ID: f2880b35e671
Revises: 7f617bc0dfc3
Create Date: 2024-09-15 14:05:06.863126

"""

import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

from alembic import op

revision = "f2880b35e671"
down_revision = "09a61aaf486d"
branch_labels = None
depends_on = None

sql_create_trigger = """
CREATE TRIGGER IF NOT EXISTS
    product_price_drop_update_updated
AFTER UPDATE ON product_price_drop
BEGIN
    UPDATE product_price_drop
    SET updated = DATETIME('now')
    WHERE product_price_drop_id = NEW.product_price_drop_id;
END;
"""

sql_drop_trigger = """
DROP TRIGGER IF EXISTS product_price_drop_update_updated;
"""


def upgrade() -> None:
    op.create_table(
        "product_price_drop",
        sa.Column(
            "product_price_drop_id",
            sqlite.INTEGER,
            primary_key=True,
            autoincrement="auto",
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
        sa.Column(
            "product_price_id",
            sqlite.INTEGER,
            sa.ForeignKey("product_price.product_price_id"),
        ),
        sa.Column("value", sqlite.DECIMAL, nullable=False),
        sa.Column("currency", sqlite.VARCHAR(1), nullable=False),
        sa.Column("original_value", sqlite.DECIMAL, nullable=False),
        sa.Column("original_currency", sqlite.VARCHAR(1), nullable=False),
        sa.Column("percentage", sqlite.DECIMAL, nullable=False),
    )
    op.execute(sql_create_trigger)


def downgrade() -> None:
    op.execute(sql_drop_trigger)
    op.drop_table("product_price_drop")
