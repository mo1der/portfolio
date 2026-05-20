import os

from dotenv import load_dotenv
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker

load_dotenv()

DEFAULT_SQLITE_URL = "sqlite:///./tickets.db"

DATABASE_URL = os.getenv("DATABASE_URL", DEFAULT_SQLITE_URL)


def create_database_engine():
    """
    Tworzy połączenie do bazy danych.

    Najpierw próbuje użyć DATABASE_URL z pliku .env.
    Jeśli MySQL nie działa albo połączenie się nie uda,
    aplikacja przechodzi awaryjnie na SQLite.
    """

    if DATABASE_URL.startswith("sqlite"):
        print("Używam SQLite.")
        return create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
        )

    try:
        engine = create_engine(DATABASE_URL)

        with engine.connect():
            pass

        print(f"Połączono z bazą: {DATABASE_URL}")
        return engine

    except Exception as error:
        print(f"Nie udało się połączyć z MySQL. Przechodzę na SQLite. Błąd: {error}")

        return create_engine(
            DEFAULT_SQLITE_URL,
            connect_args={"check_same_thread": False},
        )


engine = create_database_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


def get_db():
    db = SessionLocal()

    try:
        yield db
    finally:
        db.close()