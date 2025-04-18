from sqlalchemy import select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import exceptions
from app.auth.schemas import User


async def create_user(
	db: AsyncSession,
	username: str,
	password_hash: str,
) -> User:
	user = User(username=username, password_hash=password_hash)
	try:
		db.add(user)
		await db.commit()
		await db.refresh(user)
		return user
	except IntegrityError:
		await db.rollback()
		raise exceptions.UserAlreadyExistsError(username)


async def get_user(db: AsyncSession, username: str) -> User:
	res = await db.execute(select(User).where(User.username == username))
	user = res.scalar_one_or_none()
	if not user:
		raise exceptions.UserNotFoundError(username)
	return user
