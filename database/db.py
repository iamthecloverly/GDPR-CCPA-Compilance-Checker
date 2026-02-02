import os
from sqlalchemy import create_engine, inspect
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

# Create Base here to avoid circular imports
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
    """Context manager for database sessions"""
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
    """Initialize database tables"""
    if engine:
        # Import models here to avoid circular import at module level
        from database.models import ComplianceScan
        
        # Check if table exists and has correct schema
        inspector = inspect(engine)
        if inspector.has_table("compliance_scans"):
            # Drop the old table (WARNING: This deletes all data)
            Base.metadata.drop_all(bind=engine)
        
        # Create new table with correct schema
        Base.metadata.create_all(bind=engine)

def reset_db():
    """Reset database - drops all tables and recreates them"""
    if engine:
        from database.models import ComplianceScan
        Base.metadata.drop_all(bind=engine)
        Base.metadata.create_all(bind=engine)
