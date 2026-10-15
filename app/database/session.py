
from pathlib import Path

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker


DATABASE_PATH = (
    Path(__file__).resolve().parent.parent.parent
    / "data"
    / "serviceops.db"
)
DATABASE_PATH.parent.mkdir(parents=True, exist_ok=True)

engine = create_engine(
    f"sqlite:///{DATABASE_PATH.as_posix()}",
    connect_args={"check_same_thread": False},
)

SessionLocal = sessionmaker(
    bind=engine,
    expire_on_commit=False,
)


def get_db():
    with SessionLocal() as db:
        yield db
