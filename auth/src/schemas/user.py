from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, ConfigDict, EmailStr


class UserBase(BaseModel):
    id: UUID
    username: str
    first_name: str
    last_name: str
    email: EmailStr


class UserCreate(BaseModel):
    username: str
    password: str
    first_name: str
    last_name: str
    email: EmailStr


class UserRead(UserBase):
    id: UUID
    is_subscriber: bool
    model_config = ConfigDict(from_attributes=True)


class UserSocialAccountRead(BaseModel):
    id: UUID
    first_name: str
    last_name: str
    email: EmailStr


class UserUpdate(BaseModel):
    username: str | None = None
    first_name: str | None = None
    last_name: str | None = None
    email: EmailStr | None = None


class UserReadByAdmin(UserBase):
    is_active: bool
    is_subscriber: bool
    created_at: datetime


class UserReadBySuperUser(UserBase):
    is_superuser: bool
    is_staff: bool
    is_active: bool
    is_subscriber: bool
    created_at: datetime


class UserUpdatePassword(BaseModel):
    old_password: str
    new_password: str
    confirm_new_password: str


class UserResetPassword(BaseModel):
    new_password: str
    confirm_new_password: str


class UserEmail(BaseModel):
    email: EmailStr
