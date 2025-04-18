from datetime import datetime, timedelta, timezone
from typing import Annotated

import jwt
from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials, HTTPBearer
from jwt.exceptions import InvalidTokenError
from passlib.context import CryptContext
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import crud
from app.auth.schemas import User
from app.core import config
from app.db.connection import get_db

ALGORITHM = "HS256"
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
bearer_scheme = HTTPBearer(
	bearerFormat="JWT",
	description="Authentication scheme for JWT tokens.\n\n"
	"Use the token obtained from the `/auth/login` endpoint to access protected resources.",
	scheme_name="Bearer JWT",
)


async def authenticate_user(session: AsyncSession, username: str, password: str) -> bool:
	user = await crud.get_user(session, username)
	return pwd_context.verify(password, user.password_hash)


def get_password_hash(password: str) -> str:
	return pwd_context.hash(password)


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


async def get_current_user(
	session: Annotated[AsyncSession, Depends(get_db)],
	settings: Annotated[config.AppSettings, Depends(config.get_app_settings)],
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
		payload = jwt.decode(access_token, settings.jwt_secret.get_secret_value(), algorithms=[ALGORITHM])
		username = payload.get("sub")
		if username is None:
			raise credentials_exception
	except InvalidTokenError:
		raise credentials_exception
	user = await crud.get_user(session, username=username)
	if user is None:
		raise credentials_exception
	return user
