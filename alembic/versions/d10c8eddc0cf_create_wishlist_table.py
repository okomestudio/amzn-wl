"""Create wishlist table.

Revision ID: d10c8eddc0cf
Revises: 2f172f90298b
Create Date: 2023-07-20 23:55:12.723186

"""

import sqlalchemy as sa
from sqlalchemy.dialects import sqlite

from alembic import op

revision = "d10c8eddc0cf"
down_revision = "2f172f90298b"
branch_labels = None
depends_on = None


sql_create_trigger = """
CREATE TRIGGER IF NOT EXISTS
    wishlist_update_updated
AFTER UPDATE ON wishlist
BEGIN
    UPDATE wishlist
    SET updated = DATETIME('now')
    WHERE wishlist_id = NEW.wishlist_id;
END;
"""

sql_drop_trigger = """
DROP TRIGGER IF EXISTS wishlist_update_updated;
"""


def upgrade() -> None:
    op.create_table(
        "wishlist",
        sa.Column("wishlist_id", sqlite.VARCHAR(16), primary_key=True),
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
        sa.Column("hostname", sqlite.TEXT, sa.ForeignKey("site.hostname")),
        sa.Column("name", sqlite.TEXT, nullable=False),
    )
    op.execute(sql_create_trigger)


def downgrade() -> None:
    op.execute(sql_drop_trigger)
    op.drop_table("wishlist")
