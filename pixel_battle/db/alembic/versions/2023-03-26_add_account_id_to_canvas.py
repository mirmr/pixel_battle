"""
add account_id to canvas

Revision ID: 8b99fea83f2f
Revises:     cfd15d13a754
Create Date: 2023-03-26 23:04:01.259222
"""
import sqlalchemy as sa
from alembic import op


# revision identifiers used by Alembic
revision = "8b99fea83f2f"
down_revision = "cfd15d13a754"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.add_column("canvases", sa.Column("account_id", sa.BigInteger(), nullable=True))
    op.create_foreign_key(None, "canvases", "accounts", ["account_id"], ["id"], ondelete="SET NULL")
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_constraint("canvases_account_id_fkey", "canvases", type_="foreignkey")
    op.drop_column("canvases", "account_id")
    # ### end Alembic commands ###
