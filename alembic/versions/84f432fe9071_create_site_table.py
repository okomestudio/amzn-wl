"""create site table

Revision ID: 84f432fe9071
Revises: 7f617bc0dfc3
Create Date: 2024-09-12 11:02:57.316338

"""

import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

from alembic import op


revision = "84f432fe9071"
down_revision = None
branch_labels = None
depends_on = None


sql_create_trigger = """
CREATE TRIGGER IF NOT EXISTS
    site_update_updated
AFTER UPDATE ON site
BEGIN
    UPDATE site
    SET updated = DATETIME('now')
    WHERE hostname = NEW.hostname;
END;
"""

sql_drop_trigger = """
DROP TRIGGER IF EXISTS site_update_updated;
"""


def upgrade() -> None:
    op.create_table(
        "site",
        sa.Column("hostname", sqlite.TEXT, primary_key=True),
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
    )
    op.execute(sql_create_trigger)


def downgrade() -> None:
    op.execute(sql_drop_trigger)
    op.drop_table("site")
