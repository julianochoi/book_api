from pathlib import Path
from typing import AsyncGenerator

import pytest
from httpx import ASGITransport, AsyncClient
from polyfactory.pytest_plugin import register_fixture
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.config import AppSettings, get_app_settings
from app.db.connection import create_db, get_db
from app.main import BooksAPI, create_app
from tests import mocks

book_factory_fixture = register_fixture(mocks.BookFactory)
create_book_factory_fixture = register_fixture(mocks.CreateBookFactory)
update_book_factory_fixture = register_fixture(mocks.UpdateBookFactory)
user_factory_fixture = register_fixture(mocks.UserFactory)
user_model_factory_fixture = register_fixture(mocks.UserModelFactory)


@pytest.fixture(scope="session")
def monkeysession():
	with pytest.MonkeyPatch.context() as mp:
		yield mp


@pytest.fixture(scope="session")
def test_settings(monkeysession: pytest.MonkeyPatch) -> AppSettings:
	env_dict = {
		"ENVIRONMENT": "dev",
		"DATABASE_URL": "sqlite+aiosqlite:///./test.db",
		"JWT_SECRET": "test_secret",
		"JWT_EXPIRE_MINUTES": "30",
	}
	for key, value in env_dict.items():
		monkeysession.setenv(key.upper(), value)
	return AppSettings()


@pytest.fixture(scope="session", autouse=True)
async def app(test_settings: AppSettings) -> AsyncGenerator[BooksAPI, None]:
	app = create_app(settings=test_settings)
	app.dependency_overrides[get_app_settings] = lambda: test_settings
	yield app


@pytest.fixture(scope="session")
async def client(app: BooksAPI) -> AsyncGenerator[AsyncClient, None]:
	async with AsyncClient(
		transport=ASGITransport(app=app),
		base_url="http://test",
	) as client:
		yield client


@pytest.fixture(scope="session", autouse=True)
async def setup_db(test_settings: AppSettings) -> None:
	await create_db(test_settings)
	yield None

	db_file = Path("./test.db")
	if db_file.exists():
		db_file.unlink()


@pytest.fixture
async def db(setup_db) -> AsyncGenerator[AsyncSession, None]:
	async for session in get_db():
		yield session


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
