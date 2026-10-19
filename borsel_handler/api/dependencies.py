"""
FastAPI Dependencies
"""
from typing import Generator
from sqlalchemy.orm import Session
from borsel_handler.storage.database import SessionLocal


def get_db_session() -> Generator[Session, None, None]:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
