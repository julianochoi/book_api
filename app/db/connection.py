from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import DeclarativeBase

from app.core.config import AppSettings


class Base(DeclarativeBase):
	pass


async def create_db(app_settings: AppSettings) -> None:
	global SessionLocal
	engine = create_async_engine(app_settings.database_url)
	SessionLocal = async_sessionmaker(  # type: ignore[name-defined]
		bind=engine,
		class_=AsyncSession,
		expire_on_commit=False,
		autoflush=False,
		autocommit=False,
	)
	async with engine.begin() as conn:
		await conn.run_sync(Base.metadata.create_all)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
	async with SessionLocal() as session:  # type: ignore[name-defined]
		yield session
