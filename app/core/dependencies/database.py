from typing import Generator
from sqlalchemy.orm import Session

from app.database import SessionLocal

def get_db() -> Generator:
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# DANGEROUS: You must call Session.close() when using this function or you will overflow the pool. 
def get_db_persistent() -> Session:
    return SessionLocal()