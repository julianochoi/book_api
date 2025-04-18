from polyfactory import Use
from polyfactory.factories.pydantic_factory import ModelFactory
from polyfactory.factories.sqlalchemy_factory import SQLAlchemyFactory

from app import auth, books


class BookFactory(SQLAlchemyFactory[books.schemas.Book]):
	__set_as_default_factory_for_type__ = True


class CreateBookFactory(ModelFactory[books.models.CreateBookModel]):
	__set_as_default_factory_for_type__ = True

	title = Use(ModelFactory.__faker__.word)
	author = Use(ModelFactory.__faker__.name)
	published_date = Use(ModelFactory.__faker__.date)
	summary = Use(ModelFactory.__faker__.text)
	genre = Use(ModelFactory.__faker__.word)


class UpdateBookFactory(ModelFactory[books.models.UpdateBookModel]):
	__set_as_default_factory_for_type__ = True

	title = Use(ModelFactory.__faker__.word)
	author = Use(ModelFactory.__faker__.name)
	published_date = Use(ModelFactory.__faker__.date)
	summary = Use(ModelFactory.__faker__.text)
	genre = Use(ModelFactory.__faker__.word)


class UserFactory(SQLAlchemyFactory[auth.schemas.User]):
	__set_as_default_factory_for_type__ = True

	username = Use(SQLAlchemyFactory.__faker__.user_name)

	@classmethod
	def password_hash(cls) -> str:
		password = cls.__faker__.password(length=8)
		return auth.security.get_password_hash(password)


class UserModelFactory(ModelFactory[auth.models.UserModel]):
	__set_as_default_factory_for_type__ = True

	username = Use(ModelFactory.__faker__.user_name)
	password = Use(ModelFactory.__faker__.password, length=8)
