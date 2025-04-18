from sqlalchemy.orm import Mapped, mapped_column

from app.db.connection import Base


class User(Base):
	__tablename__ = "Users"

	id: Mapped[int] = mapped_column(primary_key=True, unique=True)
	username: Mapped[str] = mapped_column(unique=True)
	password_hash: Mapped[str]
