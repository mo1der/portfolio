from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base, sessionmaker
from app.core.settings import settings

# Bazowy URL SQLite awaryjny
DEFAULT_SQLITE_URL = "sqlite:///./tickets.db"

# Pobieramy URL bazy z settings
DATABASE_URL = settings.database_url or DEFAULT_SQLITE_URL

def create_database_engine():
    """
    Tworzy połączenie do bazy danych.
    - Testy: używają osobnej bazy SQLite z settings.database_url
    - Produkcja / development: MySQL / PostgreSQL lub SQLite
    """
    # SQLite wymaga connect_args
    if DATABASE_URL.startswith("sqlite"):
        print(f"Używam SQLite ({DATABASE_URL})")
        return create_engine(
            DATABASE_URL,
            connect_args={"check_same_thread": False},
        )

    # Inne bazy (MySQL/PostgreSQL)
    try:
        engine = create_engine(DATABASE_URL)
        # Sprawdzenie połączenia
        with engine.connect():
            pass
        print(f"Połączono z bazą: {DATABASE_URL}")
        return engine

    except Exception as error:
        print(f"Nie udało się połączyć z bazą. Przechodzę na SQLite. Błąd: {error}")
        return create_engine(
            DEFAULT_SQLITE_URL,
            connect_args={"check_same_thread": False},
        )

# --- Engine i sesje ---
engine = create_database_engine()

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

# --- Dependency dla FastAPI ---
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()