"""
Database engine, session factory, and declarative base.

Uses SQLAlchemy 2.0-style with PostgreSQL via psycopg2.
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, sessionmaker

from app.config import settings

engine = create_engine(
    settings.database_url,
    echo=settings.debug,  # Log SQL statements when debug=True
    pool_pre_ping=True,   # Verify connections before use
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    """Base class for all ORM models."""
    pass


def get_db():
    """
    FastAPI dependency that yields a database session.

    Usage:
        @app.get("/example")
        def example(db: Session = Depends(get_db)):
            ...
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
