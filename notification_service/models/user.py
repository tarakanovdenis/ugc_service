from datetime import datetime, timezone

from sqlalchemy import DateTime, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base


class User(Base):
    __tablename__ = 'users'

    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    email: Mapped[str] = mapped_column(String(32), unique=True)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    first_name: Mapped[str] = mapped_column(String(32))
    last_name: Mapped[str] = mapped_column(String(32))
    is_superuser: Mapped[bool] = mapped_column(Boolean(), default=False, server_default='0')
    is_staff: Mapped[bool] = mapped_column(Boolean(), default=False, server_default='0')
    is_active: Mapped[bool] = mapped_column(Boolean(), default=True, server_default='1')
    is_subscriber: Mapped[bool] = mapped_column(
        Boolean(), default=False, server_default="0"
    )
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
    created_at: Mapped[DateTime] = mapped_column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
    )

    repr_columns = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name'
    )
