from datetime import date

from sqlalchemy.orm import Mapped, mapped_column

from app.db.connection import Base


# NOTE should there be a unique key on title or a composite key on title and author?
class Book(Base):
	__tablename__ = "books"

	id: Mapped[int] = mapped_column(primary_key=True, unique=True)
	title: Mapped[str]
	author: Mapped[str]
	published_date: Mapped[date | None]
	summary: Mapped[str | None]
	genre: Mapped[str]
