import asyncio

from httpx import AsyncClient

from app.auth.security import create_access_token


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


async def test_jwt_expiration(client: AsyncClient) -> None:
	expired_token = create_access_token(subject="testuser", expires_in_minutes=0)
	headers = {"Authorization": f"Bearer {expired_token}"}

	await asyncio.sleep(1)  # Wait for the token to expire
	r = await client.get("/books", headers=headers)

	assert r.status_code == 401
	assert r.json() == {"detail": "Could not validate credentials"}


async def test_jwt_with_nonexistent_user(client: AsyncClient) -> None:
	non_existent_user_token = create_access_token(subject="non_existent_user")
	headers = {"Authorization": f"Bearer {non_existent_user_token}"}
	r = await client.get("/books", headers=headers)
	assert r.status_code == 401
	assert r.json() == {"detail": "Could not validate credentials"}
