from fastapi import APIRouter, Depends

from app.api import auth, books
from app.auth.security import get_current_user

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(
	router=books.router,
	dependencies=[Depends(get_current_user)],
)
