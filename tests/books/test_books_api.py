import pytest
from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from tests import mocks


@pytest.fixture
async def get_valid_user_jwt(
	client: AsyncClient,
	user_model_factory: mocks.UserModelFactory,
) -> str:
	"""Fixture to get a valid JWT token for a user."""
	user = user_model_factory.build()
	await client.post("/auth/register", json=user.model_dump())
	r = await client.post("/auth/login", json=user.model_dump())
	token = r.json()
	return token["access_token"]


async def test_create_book(
	client: AsyncClient,
	get_valid_user_jwt: str,
	create_book_factory: mocks.CreateBookFactory,
) -> None:
	book_data = create_book_factory.build()
	headers = {"Authorization": f"Bearer {get_valid_user_jwt}"}

	r = await client.post("/books", json=book_data.model_dump(mode="json"), headers=headers)

	assert r.status_code == 200
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


async def test_without_authentication(client: AsyncClient) -> None:
	r = await client.get("/books")

	assert r.status_code == 403
	assert r.json() == {"detail": "Not authenticated"}


async def test_empty_token(client: AsyncClient) -> None:
	headers = {"Authorization": "Bearer "}

	r = await client.get("/books", headers=headers)

	assert r.status_code == 403
	assert r.json() == {"detail": "Not authenticated"}


async def test_missing_bearer(
	client: AsyncClient,
	get_valid_user_jwt: str,
) -> None:
	headers = {"Authorization": f"{get_valid_user_jwt}"}

	r = await client.get("/books", headers=headers)

	assert r.status_code == 403
	assert r.json() == {"detail": "Not authenticated"}


async def test_invalid_jwt(client: AsyncClient) -> None:
	headers = {"Authorization": "Bearer invalid_token"}

	r = await client.get("/books", headers=headers)

	assert r.status_code == 401
	assert r.json() == {"detail": "Could not validate credentials"}


# TODO add jwt expiration test
