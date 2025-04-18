from typing import Sequence

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.books import exceptions
from app.books.models import CreateBookModel, UpdateBookModel
from app.books.schemas import Book


async def create_book(db: AsyncSession, book_model: CreateBookModel) -> Book:
	db_book = Book(**book_model.model_dump())
	db.add(db_book)
	await db.commit()
	await db.refresh(db_book)
	return db_book


async def get_books(
	db: AsyncSession,
	skip: int = 0,
	limit: int = 100,
) -> Sequence[Book]:
	result = await db.execute(select(Book).order_by(Book.id).offset(skip).limit(limit))
	return result.scalars().all()


async def get_book(db: AsyncSession, book_id: int) -> Book:
	"""Get a book by ID.

	Raises:
		exceptions.BookNotFoundError
	"""
	res = await db.execute(select(Book).where(Book.id == book_id))
	book = res.scalar_one_or_none()
	if not book:
		raise exceptions.BookNotFoundError(book_id)
	return book


async def update_book(db: AsyncSession, book_id: int, book_patch: UpdateBookModel) -> Book:
	db_book = await get_book(db, book_id)
	for key, value in book_patch.model_dump(exclude_unset=True).items():
		setattr(db_book, key, value)
	await db.commit()
	await db.refresh(db_book)
	return db_book


async def delete_book(db: AsyncSession, book: Book) -> None:
	await db.delete(book)
	await db.commit()
