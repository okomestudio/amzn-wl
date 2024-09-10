"""Create wishlist table.

Revision ID: d10c8eddc0cf
Revises: 2f172f90298b
Create Date: 2023-07-20 23:55:12.723186

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
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
    SET updated = DATETIME('NOW')
    WHERE wishlist_id = NEW.wishlist_id;
END;
"""

sql_drop_trigger = """
DROP TRIGGER IF EXISTS wishlist_update_updated;
"""


def upgrade() -> None:  # noqa
    op.create_table(
        "wishlist",
        sa.Column("wishlist_id", sa.String(), primary_key=True),
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
        sa.Column("name", sa.String(), nullable=False),
    )
    op.execute(sql_create_trigger)


def downgrade() -> None:  # noqa
    op.execute(sql_drop_trigger)
    op.drop_table("wishlist")
