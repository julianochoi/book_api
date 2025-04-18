from pydantic import AfterValidator, BaseModel, ConfigDict
from typing_extensions import Annotated


class Token(BaseModel):
	access_token: str
	token_type: str


def password_validator(password: str) -> str:
	if len(password) < 8:
		raise ValueError("Password must be at least 8 characters long")
	return password


class UserModel(BaseModel):
	username: str
	password: Annotated[str, AfterValidator(password_validator)]

	model_config = ConfigDict(extra="forbid")
