from datetime import datetime

from pydantic import BaseModel


class LoginHistoryBase(BaseModel):
    OS: str
    browser: str
    logged_in_at: datetime
