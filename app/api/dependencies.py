from typing import Annotated

from fastapi import Depends
from fastapi.security import HTTPAuthorizationCredentials
from sqlalchemy.ext.asyncio import AsyncSession

from app.auth.security import bearer_scheme
from app.db.connection import get_db

SessionDep = Annotated[AsyncSession, Depends(get_db)]
JWTBearerDep = Annotated[HTTPAuthorizationCredentials, Depends(bearer_scheme)]
