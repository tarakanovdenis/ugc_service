from __future__ import annotations
from typing import TYPE_CHECKING
import string
import secrets
from datetime import datetime, timezone
from uuid import uuid4

from sqlalchemy import DateTime, String, Boolean
from sqlalchemy.orm import Mapped, mapped_column, relationship
from passlib.context import CryptContext

from src.models.base import Base
from src.models.login_history import LoginHistory


pwd_context = CryptContext(schemes=['bcrypt'], deprecated='auto')


class UserSocialAccount(Base):
    __tablename__ = 'user_social_accounts'

    username: Mapped[str] = mapped_column(String(32), unique=True, nullable=True)
    email: Mapped[str] = mapped_column(String(32), unique=True, nullable=False)
    password: Mapped[str] = mapped_column(String(128), nullable=False)
    first_name: Mapped[str] = mapped_column(String(32))
    last_name: Mapped[str] = mapped_column(String(32))
    is_superuser: Mapped[bool] = mapped_column(Boolean(), default=False, server_default='0')
    is_admin: Mapped[bool] = mapped_column(Boolean(), default=False, server_default='0')
    is_active: Mapped[bool] = mapped_column(Boolean(), default=False, server_default='1')
    is_subscriber: Mapped[bool] = mapped_column(
        Boolean(), default=True, server_default="0"
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

    login_histories: Mapped[list[LoginHistory]] = relationship(
        back_populates='user_social_account',
        passive_deletes=True
    )

    repr_columns = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name'
    )

    def __init__(
            self,
            first_name: str,
            last_name: str,
            email: str,
            is_active: bool = True,
            is_staff: bool = False,
            is_superuser: bool = False,
            is_subscriber: bool = False,
    ) -> None:
        self.id = str(uuid4())
        self.password = self.get_hashed_password(
            self.get_random_password()
        )
        self.first_name = first_name
        self.last_name = last_name
        self.email = email
        self.is_active = is_active
        self.is_staff = is_staff
        self.is_superuser = is_superuser
        self.is_subscriber = is_subscriber

    def get_random_password(self, password_length: int = 8):
        alphabet = string.ascii_letters + string.digits
        password = ''.join(
            secrets.choice(alphabet) for i in range(password_length)
        )
        return password

    def get_hashed_password(self, plain_password: str) -> str:
        return pwd_context.hash(plain_password)

    def verify_password(
        self, plain_password: str, hashed_password: str
    ) -> bool:
        return pwd_context.verify(plain_password, hashed_password)