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


class UserAlreadyExistsError(UserError):
	"""Exception raised when a user already exists."""

	def __init__(self, username: str):
		super().__init__(f"User '{username}' already exists.")
		self.username = username
