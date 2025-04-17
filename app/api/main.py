from fastapi import APIRouter

from app.api import books

# TODO add jwt authentication
api_router = APIRouter()
api_router.include_router(books.router)
