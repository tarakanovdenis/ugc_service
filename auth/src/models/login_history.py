from __future__ import annotations
import uuid
from typing import TYPE_CHECKING

from sqlalchemy import (
    DateTime,
    String,
    ForeignKey,
    UniqueConstraint,
    PrimaryKeyConstraint,
    text
)
from sqlalchemy.orm import Mapped, mapped_column, relationship
from sqlalchemy.dialects.postgresql import UUID

from src.models.base import Base


if TYPE_CHECKING:
    from src.models.user import User
    from src.models.user_social_account import UserSocialAccount


def create_partition(target, connection, **kwargs) -> None:
    '''
    Creating table partition by user sign in device:
    console, mobile, tablet, smarttv, wearable, embedded, undefined
    '''
    connection.execute(
        text(
            '''
                CREATE TABLE IF NOT EXISTS 'login_histories_console'
                PARTITION OF 'login_histories'
                FOR VALUES IN ('console')
            '''
        ),
    )
    connection.execute(
        text(
            '''
                CREATE TABLE IF NOT EXISTS 'login_histories_mobile'
                PARTITION OF 'login_histories'
                FOR VALUES IN ('mobile')
            '''
        ),
    )
    connection.execute(
        text(
            '''
                CREATE TABLE IF NOT EXISTS 'login_histories_tablet'
                PARTITION OF 'login_histories'
                FOR VALUES IN ('tablet')
            '''
        ),
    )
    connection.execute(
        text(
            '''
                CREATE TABLE IF NOT EXISTS 'login_histories_smarttv'
                PARTITION OF 'login_histories'
                FOR VALUES IN ('smarttv')
            '''
        ),
    )
    connection.execute(
        text(
            '''
                CREATE TABLE IF NOT EXISTS 'login_histories_wearable'
                PARTITION OF 'login_histories'
                FOR VALUES IN ('wearable')
            '''
        ),
    )
    connection.execute(
        text(
            '''
                CREATE TABLE IF NOT EXISTS 'login_histories_embedded'
                PARTITION OF 'login_histories'
                FOR VALUES IN ('embedded')
            '''
        ),
    )
    connection.execute(
        text(
            '''
                CREATE TABLE IF NOT EXISTS 'login_histories_undefined'
                PARTITION OF 'login_histories'
                FOR VALUES IN ('undefined')
            '''
        ),
    )


class LoginHistory(Base):
    __tablename__ = 'login_histories'

    __table_args__ = (
        PrimaryKeyConstraint('id', 'device_type'),
        UniqueConstraint('id', 'device_type'),
        {
            'postgresql_partition_by': 'LIST (device_type)',
            'listeners': [('after_create', create_partition)],
        }
    )
    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        default=uuid.uuid4,
        nullable=False
    )
    OS: Mapped[str] = mapped_column(String(32), nullable=True)
    browser: Mapped[str] = mapped_column(String(32), nullable=True)
    device_type: Mapped[str] = mapped_column(String(32))
    logged_in_at: Mapped[DateTime] = mapped_column(DateTime(timezone=True))
    user_id: Mapped[UUID] = mapped_column(
        ForeignKey('users.id', ondelete='CASCADE'),
        nullable=True,
    )
    user_social_account_id: Mapped[UUID] = mapped_column(
        ForeignKey('user_social_accounts.id', ondelete='CASCADE'),
        nullable=True,
    )

    user: Mapped[User] = relationship(
        back_populates='login_histories'
    )

    user_social_account: Mapped[UserSocialAccount] = relationship(
        back_populates='login_histories',
    )

    repr_columns = (
        'id',
        'browser',
        'logged_in_at',
        'user_id'
    )
