from fastapi import APIRouter, HTTPException, status

from app.api import dependencies
from app.auth import crud, exceptions, security
from app.auth.models import Token, UserModel

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post(
	"/login",
	status_code=200,
	summary="Login user",
	responses={
		401: {
			"description": "Additional Response - Incorrect username or password",
			"model": dependencies.ExceptionModel,
			"content": {
				"application/json": {
					"example": {"detail": "Incorrect username or password"},
				}
			},
		},
		404: {
			"description": "Additional Response - User not found",
			"model": dependencies.ExceptionModel,
			"content": {
				"application/json": {
					"example": {"detail": "User 'username' not found."},
				}
			},
		},
	},
)
async def login(session: dependencies.SessionDep, form_data: UserModel) -> Token:
	"""Login user and return JWT token."""
	try:
		user_valid = await security.authenticate_user(session, form_data.username, form_data.password)
		if not user_valid:
			raise HTTPException(
				status_code=status.HTTP_401_UNAUTHORIZED,
				detail="Incorrect username or password",
			)
		access_token = security.create_access_token(subject=form_data.username)
		return Token(access_token=access_token, token_type="bearer")
	except exceptions.UserNotFoundError as e:
		raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))


@router.post(
	"/register",
	status_code=201,
	summary="Register new user",
	responses={
		status.HTTP_409_CONFLICT: {
			"description": "Additional Response - User already exists",
			"model": dependencies.ExceptionModel,
			"content": {
				"application/json": {
					"example": {"detail": "User 'username' already exists."},
				}
			},
		},
	},
)
async def register(session: dependencies.SessionDep, new_user: UserModel) -> None:
	"""Register a new user.

	Parameters:
	- username: The username of the new user. Has to be unique.
	- password: The password of the new user. Has to be at least 8 characters long.
	"""
	try:
		await crud.create_user(
			session,
			username=new_user.username,
			password_hash=security.get_password_hash(new_user.password),
		)
	except exceptions.UserAlreadyExistsError as e:
		raise HTTPException(
			status_code=status.HTTP_409_CONFLICT,
			detail=str(e),
		)
