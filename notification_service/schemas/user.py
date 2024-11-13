from uuid import UUID
from datetime import datetime

from pydantic import BaseModel, EmailStr


class User(BaseModel):
    id: UUID
    username: str
    first_name: str
    last_name: str
    email: EmailStr
    phone_number: str
    updated_at: datetime
    created_at: datetime
