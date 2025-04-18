from fastapi import APIRouter, Depends, HTTPException

from app.api import dependencies
from app.books import crud, exceptions, models

router = APIRouter(
	prefix="/books",
	tags=["books"],
	dependencies=[Depends(dependencies.get_current_user)],
)


@router.post("", status_code=201)
async def create_book(
	session: dependencies.SessionDep,
	input_book: models.CreateBookModel,
) -> models.BookResponseModel:
	"""Create a new book."""
	book = await crud.create_book(session, input_book)
	return models.BookResponseModel.model_validate(book)


@router.get("", status_code=200)
async def get_books(
	session: dependencies.SessionDep,
	skip: int = 0,
	limit: int = 100,
) -> list[models.BookResponseModel]:
	"""Get all books with pagination, ordered by id.

	NOTE: Uses **offset** pagination:
	- `skip` is the number of records to skip.
	- `limit` is the maximum number of records to return.
	"""
	books = await crud.get_books(session, skip=skip, limit=limit)
	return [models.BookResponseModel.model_validate(book) for book in books]


@router.get(
	"/{book_id}",
	status_code=200,
	responses={
		404: {
			"description": "Additional Response - Book not found",
			"model": dependencies.ExceptionModel,
			"content": {
				"application/json": {
					"example": {"detail": "Book with id 'book_id' not found."},
				}
			},
		},
	},
)
async def get_book(
	session: dependencies.SessionDep,
	book_id: int,
) -> models.BookResponseModel:
	"""Retrieves a book by book id."""
	try:
		book = await crud.get_book(session, book_id)
		return models.BookResponseModel.model_validate(book)
	except exceptions.BookNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e))


@router.patch(
	"/{book_id}",
	status_code=200,
	responses={
		404: {
			"description": "Additional Response - Book not found",
			"model": dependencies.ExceptionModel,
			"content": {
				"application/json": {
					"example": {"detail": "Book with id 'book_id' not found."},
				}
			},
		},
	},
)
async def update_book(
	session: dependencies.SessionDep,
	book_id: int,
	book_patch: models.UpdateBookModel,
) -> models.BookResponseModel:
	"""Partially update a book by id."""
	try:
		book = await crud.update_book(session, book_id, book_patch)
		return models.BookResponseModel.model_validate(book)
	except exceptions.BookNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e))


@router.delete(
	"/{book_id}",
	status_code=204,
	responses={
		404: {
			"description": "Additional Response - Book not found",
			"model": dependencies.ExceptionModel,
			"content": {
				"application/json": {
					"example": {"detail": "Book with id 'book_id' not found."},
				}
			},
		},
	},
)
async def delete_book(
	book_id: int,
	session: dependencies.SessionDep,
) -> None:
	"""Delete a book by id."""
	try:
		book = await crud.get_book(session, book_id)
		await crud.delete_book(session, book)
	except exceptions.BookNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e))
