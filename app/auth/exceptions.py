from fastapi import status
from pydantic import BaseModel


class ExceptionModel(BaseModel):
	detail: str


class UserError(Exception):
	"""Base class for user-related exceptions."""

	pass


class UserNotFoundError(UserError):
	"""Exception raised when a user is not found."""

	def __init__(self, username: str):
		super().__init__(f"User '{username}' not found.")
		self.username = username
		self.status_code = status.HTTP_404_NOT_FOUND
		self.detail = f"User '{username}' not found."


class UserAlreadyExistsError(UserError):
	"""Exception raised when a user already exists."""

	def __init__(self, username: str):
		super().__init__(f"User '{username}' already exists.")
		self.username = username
		self.status_code = status.HTTP_409_CONFLICT
		self.detail = f"User '{username}' already exists."
