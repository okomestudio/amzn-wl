"""create product_price_loyalty table

Revision ID: ffeadb986375
Revises: f2880b35e671
Create Date: 2024-09-15 14:13:24.944994

"""

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

revision = "ffeadb986375"
down_revision = "f2880b35e671"
branch_labels = None
depends_on = None


sql_create_trigger = """
CREATE TRIGGER IF NOT EXISTS
    product_price_loyalty_update_updated
AFTER UPDATE ON product_price_loyalty
BEGIN
    UPDATE product_price_loyalty
    SET updated = DATETIME('now')
    WHERE product_price_loyalty_id = NEW.product_price_loyalty_id;
END;
"""

sql_drop_trigger = """
DROP TRIGGER IF EXISTS product_price_loyalty_update_updated;
"""


def upgrade() -> None:
    op.create_table(
        "product_price_loyalty",
        sa.Column(
            "product_price_loyalty_id",
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
        sa.Column("point", sqlite.DECIMAL, nullable=False),
        sa.Column("percentage", sqlite.DECIMAL, nullable=False),
    )
    op.execute(sql_create_trigger)


def downgrade() -> None:
    op.execute(sql_drop_trigger)
    op.drop_table("product_price_loyalty")
