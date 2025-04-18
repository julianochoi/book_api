from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests import mocks


async def test_create_book(
	client: AsyncClient,
	get_valid_user_jwt: str,
	create_book_factory: mocks.CreateBookFactory,
) -> None:
	book_data = create_book_factory.build()
	headers = {"Authorization": f"Bearer {get_valid_user_jwt}"}

	r = await client.post("/books", json=book_data.model_dump(mode="json"), headers=headers)

	assert r.status_code == 201
	assert r.json() is not None
	assert r.json()["title"] == book_data.title
	assert r.json()["author"] == book_data.author


async def test_get_books(
	db: AsyncSession,
	client: AsyncClient,
	get_valid_user_jwt: str,
	book_factory: mocks.BookFactory,
) -> None:
	book_factory.__async_session__ = db
	await book_factory.create_batch_async(10)
	headers = {"Authorization": f"Bearer {get_valid_user_jwt}"}

	r = await client.get("/books", headers=headers)

	assert r.status_code == 200
	assert len(r.json()) >= 10


async def test_get_book(
	db: AsyncSession,
	client: AsyncClient,
	get_valid_user_jwt: str,
	book_factory: mocks.BookFactory,
) -> None:
	book_factory.__async_session__ = db
	book = await book_factory.create_async()
	headers = {"Authorization": f"Bearer {get_valid_user_jwt}"}

	r = await client.get(f"/books/{book.id}", headers=headers)

	assert r.status_code == 200
	assert r.json() is not None
	assert r.json()["id"] == book.id
	assert r.json()["title"] == book.title
	assert r.json()["author"] == book.author


async def test_get_book_not_found(
	client: AsyncClient,
	get_valid_user_jwt: str,
) -> None:
	headers = {"Authorization": f"Bearer {get_valid_user_jwt}"}
	invalid_book_id = 999999

	r = await client.get(f"/books/{invalid_book_id}", headers=headers)

	assert r.status_code == 404
	assert r.json() == {"detail": f"Book with id {invalid_book_id} not found."}


async def test_update_book(
	db: AsyncSession,
	client: AsyncClient,
	get_valid_user_jwt: str,
	book_factory: mocks.BookFactory,
) -> None:
	book_factory.__async_session__ = db
	book = await book_factory.create_async()
	headers = {"Authorization": f"Bearer {get_valid_user_jwt}"}
	updated_data = {"title": "Updated Title", "author": "Updated Author"}

	r = await client.patch(f"/books/{book.id}", json=updated_data, headers=headers)

	assert r.status_code == 200
	assert r.json() is not None
	assert r.json()["id"] == book.id
	assert r.json()["title"] == updated_data["title"]
	assert r.json()["author"] == updated_data["author"]


async def test_update_book_not_found(
	client: AsyncClient,
	get_valid_user_jwt: str,
) -> None:
	headers = {"Authorization": f"Bearer {get_valid_user_jwt}"}
	invalid_book_id = 999999
	updated_data = {"title": "Updated Title", "author": "Updated Author"}

	r = await client.patch(f"/books/{invalid_book_id}", json=updated_data, headers=headers)

	assert r.status_code == 404
	assert r.json() == {"detail": f"Book with id {invalid_book_id} not found."}


async def test_delete_book(
	db: AsyncSession,
	client: AsyncClient,
	get_valid_user_jwt: str,
	book_factory: mocks.BookFactory,
) -> None:
	book_factory.__async_session__ = db
	book = await book_factory.create_async()
	headers = {"Authorization": f"Bearer {get_valid_user_jwt}"}

	r = await client.delete(f"/books/{book.id}", headers=headers)

	assert r.status_code == 204

	# Verify the book is deleted
	r = await client.get(f"/books/{book.id}", headers=headers)
	assert r.status_code == 404
	assert r.json() == {"detail": f"Book with id {book.id} not found."}


async def test_delete_book_not_found(
	client: AsyncClient,
	get_valid_user_jwt: str,
) -> None:
	headers = {"Authorization": f"Bearer {get_valid_user_jwt}"}
	invalid_book_id = 999999

	r = await client.delete(f"/books/{invalid_book_id}", headers=headers)

	assert r.status_code == 404
	assert r.json() == {"detail": f"Book with id {invalid_book_id} not found."}
