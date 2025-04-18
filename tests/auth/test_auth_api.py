from httpx import AsyncClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import decode_access_token
from tests import mocks


async def test_register_user(
	client: AsyncClient,
	user_model_factory: mocks.UserModelFactory,
) -> None:
	login_data = user_model_factory.build()
	r = await client.post("/auth/register", json=login_data.model_dump())
	assert r.status_code == 201
	assert r.json() is None


async def test_register_user_already_exists(
	client: AsyncClient,
	user_model_factory: mocks.UserModelFactory,
) -> None:
	login_data = user_model_factory.build()
	await client.post("/auth/register", json=login_data.model_dump())

	r = await client.post("/auth/register", json=login_data.model_dump())

	assert r.status_code == 409
	assert r.json() == {"detail": f"User '{login_data.username}' already exists."}


async def test_register_user_invalid_password(client: AsyncClient) -> None:
	login_data = {"username": "testuser", "password": "short"}

	r = await client.post("/auth/register", json=login_data)

	assert r.status_code == 422


async def test_get_access_token(
	db: AsyncSession,
	client: AsyncClient,
	user_model_factory: mocks.UserModelFactory,
) -> None:
	user = user_model_factory.build()
	await client.post("/auth/register", json=user.model_dump())

	r = await client.post("/auth/login", json=user.model_dump())
	token = r.json()
	token_data = decode_access_token(token["access_token"])

	assert r.status_code == 200
	assert token["token_type"] == "bearer"
	assert token_data["sub"] == user.username
	assert token_data["iat"] is not None
	assert token_data["exp"] is not None


async def test_login_with_user_not_found(
	client: AsyncClient,
) -> None:
	login_data = {
		"username": "nonexistentuser",
		"password": "password123",
	}
	r = await client.post("/auth/login", json=login_data)

	assert r.status_code == 404
	assert r.json() == {"detail": f"User '{login_data['username']}' not found."}


async def test_login_with_incorrect_password(
	client: AsyncClient,
	user_model_factory: mocks.UserModelFactory,
) -> None:
	login_data = user_model_factory.build()
	await client.post("/auth/register", json=login_data.model_dump())

	incorrect_password = {"username": login_data.username, "password": "wrongpassword"}
	r = await client.post("/auth/login", json=incorrect_password)

	assert r.status_code == 401
	assert r.json() == {"detail": "Incorrect username or password"}
