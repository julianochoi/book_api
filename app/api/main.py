from fastapi import APIRouter

from app.api import auth, books

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(router=books.router)
