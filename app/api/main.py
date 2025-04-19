from fastapi import APIRouter

from app.api import auth, books, sse

api_router = APIRouter()
api_router.include_router(auth.router)
api_router.include_router(router=books.router)
api_router.include_router(sse.router)
