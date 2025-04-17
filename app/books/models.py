from datetime import date

from pydantic import BaseModel, ConfigDict


class CreateBookModel(BaseModel):
	title: str
	author: str
	published_date: date | None = None
	summary: str | None = None
	genre: str

	model_config = ConfigDict(extra="forbid")


class BookResponseModel(BaseModel):
	id: int
	title: str
	author: str
	published_date: date | None = None
	summary: str | None = None
	genre: str

	model_config = ConfigDict(from_attributes=True, extra="ignore")


class UpdateBookModel(BaseModel):
	title: str | None = None
	author: str | None = None
	published_date: date | None = None
	summary: str | None = None
	genre: str | None = None

	model_config = ConfigDict(extra="forbid")
