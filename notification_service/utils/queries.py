from sqlalchemy import Result

from models.user import User
from db.database import Session


def get_users() -> Result:
    with Session() as session:
        users_orm: Result = session.query(User).all()
        return users_orm
