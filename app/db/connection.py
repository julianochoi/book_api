from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

from app.core.config import AppSettings


class Base(DeclarativeBase):
	pass


# TODO veriyfy if async version is needed
def create_db(app_settings: AppSettings) -> None:
	engine = create_engine(app_settings.db_conn_url)
	global SessionLocal
	SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)  # type: ignore
	Base.metadata.create_all(bind=engine)


def get_db() -> Generator[Session, None, None]:
	db = SessionLocal()  # type: ignore
	try:
		yield db
	finally:
		db.close()
