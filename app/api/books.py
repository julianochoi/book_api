from fastapi import APIRouter, Depends, HTTPException

from app.api import dependencies
from app.books import crud, exceptions, models
from app.db.redis import publish_event

router = APIRouter(
	prefix="/books",
	tags=["books"],
	dependencies=[Depends(dependencies.get_current_user)],
)

REDIS_BOOK_CHANNEL = "books"


@router.post("", status_code=201)
async def create_book(
	session: dependencies.SessionDep,
	redis: dependencies.RedisDep,
	input_book: models.CreateBookModel,
	user: dependencies.UserDep,
) -> models.BookResponseModel:
	"""Create a new book."""
	book = await crud.create_book(session, input_book)
	response = models.BookResponseModel.model_validate(book)

	await publish_event(
		redis,
		channel=REDIS_BOOK_CHANNEL,
		event_type="book_created",
		event_data=response.model_dump(mode="json", include={"id", "title", "author"}),
		username=user.username,
	)
	return response


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
	redis: dependencies.RedisDep,
	user: dependencies.UserDep,
	book_id: int,
	book_patch: models.UpdateBookModel,
) -> models.BookResponseModel:
	"""Partially update a book by id."""
	try:
		book = await crud.update_book(session, book_id, book_patch)
		response = models.BookResponseModel.model_validate(book)

		# NOTE include only the fields that were updated and the id
		fields_to_keep = book_patch.model_fields_set.union({"id"})
		await publish_event(
			redis,
			channel=REDIS_BOOK_CHANNEL,
			event_type="book_updated",
			event_data=response.model_dump(mode="json", include=fields_to_keep),
			username=user.username,
		)
		return response
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
	redis: dependencies.RedisDep,
	user: dependencies.UserDep,
) -> None:
	"""Delete a book by id."""
	try:
		book = await crud.get_book(session, book_id)
		await crud.delete_book(session, book)
		await publish_event(
			redis,
			channel=REDIS_BOOK_CHANNEL,
			event_type="book_deleted",
			event_data={"id": book_id},
			username=user.username,
		)
	except exceptions.BookNotFoundError as e:
		raise HTTPException(status_code=404, detail=str(e))
