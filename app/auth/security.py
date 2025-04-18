from datetime import datetime, timedelta, timezone
from typing import Any

import bcrypt
import jwt
from fastapi.security import HTTPBearer
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import crud
from app.core import config

ALGORITHM = "HS256"
bearer_scheme = HTTPBearer(
	bearerFormat="JWT",
	description="Authentication scheme for JWT tokens.\n\n"
	"Use the token obtained from the `/auth/login` endpoint to access protected resources.",
	scheme_name="Bearer JWT",
	auto_error=True,
)


async def authenticate_user(session: AsyncSession, username: str, password: str) -> bool:
	user = await crud.get_user(session, username)
	return bcrypt.checkpw(
		password=password.encode("utf-8"),
		hashed_password=user.password_hash.encode("utf-8"),
	)


def get_password_hash(password: str) -> str:
	return bcrypt.hashpw(
		password=password.encode("utf-8"),
		salt=bcrypt.gensalt(),
	).decode("utf-8")


def create_access_token(subject: str, expires_in_minutes: int | None = None) -> str:
	settings = config.get_app_settings()
	now = datetime.now(timezone.utc)

	if expires_in_minutes is not None:
		expire = now + timedelta(minutes=expires_in_minutes)
	else:
		expire = now + timedelta(minutes=settings.jwt_expire_minutes)
	to_encode = {
		"sub": subject,
		"iat": now,
		"exp": expire,
	}
	encoded_jwt = jwt.encode(
		payload=to_encode,
		key=settings.jwt_secret.get_secret_value(),
		algorithm=ALGORITHM,
	)
	return encoded_jwt


def decode_access_token(token: str) -> Any:
	settings = config.get_app_settings()
	return jwt.decode(
		jwt=token,
		key=settings.jwt_secret.get_secret_value(),
		algorithms=[ALGORITHM],
	)
