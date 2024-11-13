"""create initial tables

Revision ID: 29d7ba882253
Revises:
Create Date: 2024-11-11 19:42:08.861911

"""

from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "29d7ba882253"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user_social_accounts",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("username", sa.String(length=32), nullable=True),
        sa.Column("email", sa.String(length=32), nullable=False),
        sa.Column("first_name", sa.String(length=32), nullable=False),
        sa.Column("last_name", sa.String(length=32), nullable=False),
        sa.Column("password", sa.String(length=128), nullable=False),
        sa.Column(
            "is_superuser", sa.Boolean(), server_default="0", nullable=False
        ),
        sa.Column(
            "is_admin", sa.Boolean(), server_default="0", nullable=False
        ),
        sa.Column(
            "is_active", sa.Boolean(), server_default="1", nullable=False
        ),
        sa.Column(
            "is_subscriber", sa.Boolean(), server_default="0", nullable=False
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_user_social_accounts")),
        sa.UniqueConstraint(
            "email", name=op.f("uq_user_social_accounts_email")
        ),
        sa.UniqueConstraint("id", name=op.f("uq_user_social_accounts_id")),
        sa.UniqueConstraint(
            "username", name=op.f("uq_user_social_accounts_username")
        ),
    )
    op.create_table(
        "users",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("username", sa.String(length=32), nullable=False),
        sa.Column("email", sa.String(length=32), nullable=False),
        sa.Column("password", sa.String(length=128), nullable=False),
        sa.Column("first_name", sa.String(length=32), nullable=False),
        sa.Column("last_name", sa.String(length=32), nullable=False),
        sa.Column(
            "is_superuser", sa.Boolean(), server_default="0", nullable=False
        ),
        sa.Column(
            "is_staff", sa.Boolean(), server_default="0", nullable=False
        ),
        sa.Column(
            "is_active", sa.Boolean(), server_default="1", nullable=False
        ),
        sa.Column(
            "is_subscriber", sa.Boolean(), server_default="0", nullable=False
        ),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_users")),
        sa.UniqueConstraint("email", name=op.f("uq_users_email")),
        sa.UniqueConstraint("id", name=op.f("uq_users_id")),
        sa.UniqueConstraint("username", name=op.f("uq_users_username")),
    )
    op.create_table(
        "login_histories",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("OS", sa.String(length=32), nullable=True),
        sa.Column("browser", sa.String(length=32), nullable=True),
        sa.Column("device_type", sa.String(length=32), nullable=False),
        sa.Column("logged_in_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=True),
        sa.Column("user_social_account_id", sa.UUID(), nullable=True),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_login_histories_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.ForeignKeyConstraint(
            ["user_social_account_id"],
            ["user_social_accounts.id"],
            name=op.f(
                "fk_login_histories_user_social_account_id_user_social_accounts"
            ),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint(
            "id", "device_type", name=op.f("pk_login_histories")
        ),
        sa.UniqueConstraint(
            "id", "device_type", name=op.f("uq_login_histories_id_device_type")
        ),
        postgresql_partition_by="LIST (device_type)",
    )
    op.create_table(
        "refresh_tokens",
        sa.Column("id", sa.UUID(), nullable=False),
        sa.Column("user_id", sa.UUID(), nullable=False),
        sa.ForeignKeyConstraint(
            ["user_id"],
            ["users.id"],
            name=op.f("fk_refresh_tokens_user_id_users"),
            ondelete="CASCADE",
        ),
        sa.PrimaryKeyConstraint("id", name=op.f("pk_refresh_tokens")),
        sa.UniqueConstraint("id", name=op.f("uq_refresh_tokens_id")),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("refresh_tokens")
    op.drop_table("login_histories")
    op.drop_table("users")
    op.drop_table("user_social_accounts")
    # ### end Alembic commands ###