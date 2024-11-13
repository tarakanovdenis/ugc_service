import uuid

from sqlalchemy.orm import (
    DeclarativeBase, Mapped, mapped_column, declared_attr
)
from sqlalchemy.dialects.postgresql import UUID


class Base(DeclarativeBase):
    __abstract__ = True

    @declared_attr
    def __tablename__(cls) -> str:
        return f'{cls.__name__.lower()}s'

    id: Mapped[UUID] = mapped_column(
        UUID(as_uuid=True),
        primary_key=True,
        default=uuid.uuid4,
        unique=True,
        nullable=False
    )

    repr_column_number = 1
    repr_columns = tuple()

    def __repr__(self):
        columns = []

        for idx, column in enumerate(self.__table__.columns.keys()):
            if column in self.repr_columns or idx < self.repr_column_number:
                columns.append(f'{column}={getattr(self, column)}')

        return f"<{self.__class__.__name__} {', '.join(columns)}>"
