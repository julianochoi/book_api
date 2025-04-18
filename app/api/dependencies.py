from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import HTTPAuthorizationCredentials
from jwt.exceptions import InvalidTokenError
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth import crud, exceptions
from app.auth.schemas import User
from app.auth.security import bearer_scheme, decode_access_token
from app.db.connection import get_db

SessionDep = Annotated[AsyncSession, Depends(get_db)]
JWTBearerDep = Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]


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
	try:
		payload = decode_access_token(access_token)
		username = payload.get("sub")
	except InvalidTokenError:
		raise credentials_exception
	try:
		user = await crud.get_user(session, username=username)
	except exceptions.UserNotFoundError:
		raise credentials_exception
	return user


UserDep = Annotated[User, Depends(get_current_user)]


class ExceptionModel(BaseModel):
	detail: str
