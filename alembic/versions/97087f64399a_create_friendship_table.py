"""Create friendship table

Revision ID: 97087f64399a
Revises: 19d985747cb1
Create Date: 2022-05-15 17:42:38.453298

"""
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

from alembic import op

# revision identifiers, used by Alembic.
revision = "97087f64399a"
down_revision = "19d985747cb1"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "friendship",
        sa.Column("user_1_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.Column("user_2_id", postgresql.UUID(as_uuid=True), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_1_id"],
            ["user.id"],
        ),
        sa.ForeignKeyConstraint(
            ["user_2_id"],
            ["user.id"],
        ),
        sa.PrimaryKeyConstraint("user_1_id", "user_2_id"),
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("friendship")
    # ### end Alembic commands ###