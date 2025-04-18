from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import SessionDep, get_current_user
from app.books import crud, exceptions, models

router = APIRouter(
	prefix="/books",
	tags=["books"],
	dependencies=[Depends(get_current_user)],
)

# TODO add better docs for each endpoint


@router.post("")
async def create_book(
	session: SessionDep,
	input_book: models.CreateBookModel,
) -> models.BookResponseModel:
	book = await crud.create_book(session, input_book)
	return models.BookResponseModel.model_validate(book)


@router.get("")
async def get_books(
	session: SessionDep,
	skip: int = 0,
	limit: int = 100,
) -> list[models.BookResponseModel]:
	"""Get all books with pagination, ordered by id.

	NOTE: Uses **offset** pagination:
	- `skip` is the number of records to skip
	- `limit` is the maximum number of records to return
	"""
	books = await crud.get_books(session, skip=skip, limit=limit)
	return [models.BookResponseModel.model_validate(book) for book in books]


@router.get("/{book_id}")
async def get_book(
	session: SessionDep,
	book_id: int,
) -> models.BookResponseModel:
	"""Get book by id."""
	try:
		book = await crud.get_book(session, book_id)
		return models.BookResponseModel.model_validate(book)
	except exceptions.BookNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e))


@router.patch("/{book_id}")
async def update_book(
	session: SessionDep,
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
)
async def delete_book(
	book_id: int,
	session: SessionDep,
) -> None:
	try:
		book = await crud.get_book(session, book_id)
		await crud.delete_book(session, book)
	except exceptions.BookNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e))
