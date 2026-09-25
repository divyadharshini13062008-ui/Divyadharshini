from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import (
    DeclarativeBase,
    sessionmaker,
)

from app.config import settings


if settings.database_url.startswith("sqlite:///"):
    database_path = settings.database_url.replace(
        "sqlite:///",
        "",
        1,
    )

    Path(database_path).parent.mkdir(
        parents=True,
        exist_ok=True,
    )


connect_args = {}

if settings.database_url.startswith("sqlite"):
    connect_args = {
        "check_same_thread": False
    }


engine = create_engine(
    settings.database_url,
    connect_args=connect_args,
)


SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


class Base(DeclarativeBase):
    pass


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()


def init_db():
    from app.models.entities import (
        RecommendationHistory,
        User,
    )

    Base.metadata.create_all(
        bind=engine
    )