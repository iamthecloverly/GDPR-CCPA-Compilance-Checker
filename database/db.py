import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

# Create Base here, don't import from models
Base = declarative_base()

DATABASE_URL = os.getenv("DATABASE_URL")

if DATABASE_URL:
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
        # Import models here to avoid circular import
        from database.models import ComplianceScan
        Base.metadata.create_all(bind=engine)
