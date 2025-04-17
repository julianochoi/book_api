from sqlalchemy.orm import Session

from app.books.models import CreateBookModel, UpdateBookModel
from app.books.schemas import Book


def create_book(db: Session, book_model: CreateBookModel) -> Book:
	db_book = Book(**book_model.model_dump())
	db.add(db_book)
	db.commit()
	db.refresh(db_book)
	return db_book


def get_books(
	db: Session,
	skip: int = 0,
	limit: int = 100,
) -> list[Book]:
	return db.query(Book).order_by(Book.id).offset(skip).limit(limit).all()


def get_book(db: Session, book_id: int) -> Book | None:
	return db.query(Book).where(Book.id == book_id).first()


def update_book(db: Session, book_id: int, book_patch: UpdateBookModel) -> Book | None:
	db_book = get_book(db, book_id)
	if not db_book:
		return None
	for key, value in book_patch.model_dump(exclude_unset=True).items():
		setattr(db_book, key, value)
	db.commit()
	db.refresh(db_book)
	return db_book


def delete_book(db: Session, book: Book) -> None:
	db.delete(book)
	db.commit()
