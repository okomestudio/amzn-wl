"""create currency table

Revision ID: d01bf8db3764
Revises: ffeadb986375
Create Date: 2024-10-18 21:52:56.499906

"""

import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

from alembic import op

revision = "d01bf8db3764"
down_revision = "ffeadb986375"
branch_labels = None
depends_on = None


sql_create_trigger = """
CREATE TRIGGER IF NOT EXISTS
    currency_update_updated
AFTER UPDATE ON currency
BEGIN
    UPDATE currency
    SET updated = DATETIME('now')
    WHERE currency_id = NEW.currency_id;
END;
"""

sql_drop_trigger = """
DROP TRIGGER IF EXISTS currency_update_updated;
"""


def upgrade() -> None:
    op.create_table(
        "currency",
        sa.Column(
            "currency_id", sqlite.INTEGER, primary_key=True, autoincrement="auto"
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
        sa.Column("code", sqlite.VARCHAR(3), nullable=False),
        sa.Column("symbol", sqlite.VARCHAR(6), nullable=False),
    )
    op.execute(sql_create_trigger)

    op.execute("INSERT INTO currency (code, symbol) VALUES ('USD', '$')")
    op.execute("INSERT INTO currency (code, symbol) VALUES ('JPY', '¥')")


def downgrade() -> None:
    op.execute(sql_drop_trigger)
    op.drop_table("currency")
