from datetime import datetime, timedelta, timezone
from typing import Annotated, Any

import bcrypt
import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import crud
from app.auth.schemas import User
from app.core import config
from app.db.connection import get_db

ALGORITHM = "HS256"
bearer_scheme = HTTPBearer(
	bearerFormat="JWT",
	description="Authentication scheme for JWT tokens.\n\n"
	"Use the token obtained from the `/auth/login` endpoint to access protected resources.",
	scheme_name="Bearer JWT",
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


def create_access_token(subject: str) -> str:
	settings = config.get_app_settings()
	now = datetime.now(timezone.utc)
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


async def get_current_user(
	session: Annotated[AsyncSession, Depends(get_db)],
	credentials: Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)],
) -> User:
	"""Get current user from JWT token."""
	credentials_exception = HTTPException(
		status_code=status.HTTP_401_UNAUTHORIZED,
		detail="Could not validate credentials",
		headers={"WWW-Authenticate": "Bearer"},
	)

	access_token = credentials.credentials
	if not access_token:
		raise credentials_exception

	try:
		payload = decode_access_token(access_token)
		username = payload.get("sub")
		if username is None:
			raise credentials_exception
	except InvalidTokenError:
		raise credentials_exception
	user = await crud.get_user(session, username=username)
	if user is None:
		raise credentials_exception
	return user
