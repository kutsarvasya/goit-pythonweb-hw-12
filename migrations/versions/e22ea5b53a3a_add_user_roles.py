"""add user roles

Revision ID: e22ea5b53a3a
Revises: 752835ef3901
Create Date: 2026-05-14 19:39:15.057884

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa

# revision identifiers, used by Alembic.
revision: str = "e22ea5b53a3a"
down_revision: Union[str, Sequence[str], None] = "752835ef3901"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    userrole = sa.Enum("USER", "ADMIN", name="userrole")
    userrole.create(op.get_bind(), checkfirst=True)

    op.add_column(
        "users",
        sa.Column(
            "role",
            userrole,
            nullable=False,
            server_default="USER",
        ),
    )

    op.alter_column(
        "users",
        "role",
        server_default=None,
    )


def downgrade() -> None:
    op.drop_column("users", "role")

    userrole = sa.Enum("USER", "ADMIN", name="userrole")
    userrole.drop(op.get_bind(), checkfirst=True)  # ### end Alembic commands ###
