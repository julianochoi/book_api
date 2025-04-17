from fastapi import APIRouter, HTTPException

from app.api.dependencies import SessionDep
from app.books import crud, models

router = APIRouter(prefix="/books", tags=["books"])


@router.post("")
async def create_book(
	session: SessionDep,
	book: models.CreateBookModel,
) -> models.BookResponseModel:
	try:
		return crud.create_book(session, book)  # type: ignore # NOTE mypy doesn't recognize the return type
	except Exception as e:
		raise HTTPException(
			status_code=500,
			detail=f"Failed to create book: {str(e)}",
		)


@router.get("")
async def get_books(
	session: SessionDep,
	skip: int = 0,
	limit: int = 100,
) -> list[models.BookResponseModel]:
	"""Get all books with pagination."""
	try:
		return crud.get_books(session, skip=skip, limit=limit)  # type: ignore
	except Exception as e:
		raise HTTPException(
			status_code=500,
			detail=f"Failed to retrieve books: {str(e)}",
		)


@router.get("/{book_id}")
async def get_book(
	session: SessionDep,
	book_id: int,
) -> models.BookResponseModel:
	try:
		book = crud.get_book(session, book_id)
		if not book:
			raise HTTPException(status_code=404, detail=f"Book id={book_id} not found")
		return book  # type: ignore
	except HTTPException as e:
		raise e
	except Exception as e:
		raise HTTPException(
			status_code=500,
			detail=f"Failed to retrieve book id={book_id}: {str(e)}",
		)


@router.patch("/{book_id}")
async def update_book(
	session: SessionDep,
	book_id: int,
	book_patch: models.UpdateBookModel,
) -> models.BookResponseModel:
	try:
		book = crud.update_book(session, book_id, book_patch)
		if not book:
			raise HTTPException(status_code=404, detail=f"Book id={book_id} not found")
		return book  # type: ignore
	except HTTPException as e:
		raise e
	except Exception as e:
		raise HTTPException(
			status_code=500,
			detail=f"Failed to update book id={book_id}: {str(e)}",
		)


@router.delete(
	"/{book_id}",
	status_code=204,
)
async def delete_book(
	book_id: int,
	session: SessionDep,
) -> None:
	try:
		book = crud.get_book(session, book_id)
		if not book:
			raise HTTPException(status_code=404, detail=f"Book id={book_id} not found")
		crud.delete_book(session, book)
	except HTTPException as e:
		raise e
	except Exception as e:
		raise HTTPException(
			status_code=500,
			detail=f"Failed to delete book id={book_id}: {str(e)}",
		)
