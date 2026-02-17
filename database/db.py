import os
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.orm import sessionmaker, declarative_base
from contextlib import contextmanager

# Create Base here to avoid circular imports
Base = declarative_base()

DATABASE_URL = os.getenv("DATABASE_URL")

def _create_engine(db_url: str):
    if db_url.startswith("sqlite"):
        return create_engine(
            db_url,
            connect_args={"check_same_thread": False}
        )

    connect_args = {}
    # Only enforce SSL for postgresql if not explicit
    if db_url.startswith("postgresql") and "sslmode=" not in db_url:
        connect_args["sslmode"] = "require"

    return create_engine(
        db_url,
        pool_pre_ping=True,
        pool_recycle=300,
        connect_args=connect_args
    )

if DATABASE_URL:
    db_url = DATABASE_URL.replace("&channel_binding=require", "").replace("?channel_binding=require", "")
    engine = _create_engine(db_url)
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
        try:
            # Import models here to avoid circular import at module level
            from database.models import ComplianceScan
            
            # Check if table exists
            inspector = inspect(engine)
            
            if inspector.has_table("compliance_scans"):
                # Check if table has correct columns
                columns = [col['name'] for col in inspector.get_columns("compliance_scans")]
                required_columns = ['id', 'url', 'score', 'grade', 'status', 
                                   'cookie_consent', 'privacy_policy', 'contact_info', 
                                   'trackers', 'scan_date', 'ai_analysis']
                
                # If schema is incorrect, drop and recreate
                if not all(col in columns for col in required_columns):
                    with engine.connect() as conn:
                        conn.execute(text("DROP TABLE IF EXISTS compliance_scans CASCADE"))
                        conn.commit()
                    Base.metadata.create_all(bind=engine)
            else:
                # Table doesn't exist, create it
                Base.metadata.create_all(bind=engine)
                
        except Exception as e:
            # If any error, try to create fresh
            Base.metadata.create_all(bind=engine)

def reset_db():
    """Reset database - drops all tables and recreates them"""
    if engine:
        try:
            from database.models import ComplianceScan
            
            # Use raw SQL to drop table if exists
            with engine.connect() as conn:
                conn.execute(text("DROP TABLE IF EXISTS compliance_scans CASCADE"))
                conn.commit()
            
            # Create new table
            Base.metadata.create_all(bind=engine)
            
        except Exception as e:
            raise Exception(f"Failed to reset database: {str(e)}")
