import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from contextlib import contextmanager

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
    # Remove channel_binding for SQLAlchemy compatibility
    db_url = DATABASE_URL.replace("&channel_binding=require", "").replace("?channel_binding=require", "")
    
    engine = create_engine(
        db_url,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args={"sslmode": "require"}
    )
    SessionLocal = sessionmaker(bind=engine)
else:
    engine = None
    SessionLocal = None

@contextmanager
def get_db():
    if SessionLocal is None:
        yield None
        return
    
    db = SessionLocal()
    try:
        yield db
        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()

def init_db():
    if engine:
        from database.models import Base
        Base.metadata.create_all(bind=engine)
