from contextlib import asynccontextmanager
from typing import AsyncGenerator

import uvicorn
from fastapi import FastAPI
from fastapi.responses import RedirectResponse

from app.api import api_router
from app.core import config
from app.db.connection import create_db


class BooksAPI(FastAPI):
	settings: config.AppSettings


@asynccontextmanager
async def lifespan(app: BooksAPI) -> AsyncGenerator[None, None]:
	# startup
	create_db(app.settings)
	yield
	# shutdown


def create_app(settings: config.AppSettings | None = None) -> BooksAPI:
	if settings is None:
		settings = config.get_app_settings()

	app = BooksAPI(
		title="BooksAPI",
		description="API to handle and serve book data.",
		contact={"name": "Juliano Choi", "email": "julianochoi@gmail.com"},
		redoc_url=None,
		lifespan=lifespan,
	)
	app.settings = settings

	# Redirect root to docs page
	@app.get("/", include_in_schema=False)
	def docs_redirect() -> RedirectResponse:
		return RedirectResponse(url="/docs")

	app.include_router(api_router)
	return app


def main() -> None:
	settings = config.get_app_settings()
	in_dev_env = settings.environment.lower() != "prod"
	uvicorn.run(
		app="app.main:create_app",
		factory=True,
		host="0.0.0.0",
		access_log=in_dev_env,
		reload=in_dev_env,
		reload_dirs="app",
		server_header=False,
	)
