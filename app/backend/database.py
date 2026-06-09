"""
MEDHA Backend — Database Setup
SQLAlchemy engine, session factory, and Base declaration.
Uses SQLite for MVP (zero setup, file-based).
"""

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False},  # SQLite needs this for FastAPI
    echo=False,
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()


def get_db():
    """FastAPI dependency — yields a DB session, closes on completion."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Called once at startup."""
    from models import Student, Session, QuestionResult, Question, CumulativeProfile  # noqa
    Base.metadata.create_all(bind=engine)
