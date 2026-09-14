from sqlalchemy.orm import Session
from core.database import get_db

def test_get_db():
    db_gen = get_db()
    db = next(db_gen)
    assert isinstance(db, Session)
    try:
        next(db_gen)
    except StopIteration:
        pass
