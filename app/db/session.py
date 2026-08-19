import logging
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from app.core.config import settings

logger = logging.getLogger("uvicorn.error")

# SQLAlchemy Declarative Base for models
Base = declarative_base()

def create_db_engine():
    db_url = settings.DATABASE_URL
    try:
        if db_url.startswith("sqlite"):
            return create_engine(db_url, connect_args={"check_same_thread": False}, echo=False)
        else:
            # SQL Server with pyodbc connection pool
            return create_engine(
                db_url,
                pool_pre_ping=True,
                pool_recycle=3600,
                echo=False
            )
    except Exception as e:
        logger.error(f"Failed to initialize database engine with URL {db_url}: {e}")
        # Fallback to sqlite if SQL server connection string fails in standalone test
        logger.warning("Falling back to local SQLite engine.")
        return create_engine("sqlite:///./medical_assistant_fallback.db", connect_args={"check_same_thread": False})

engine = create_db_engine()
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# FastAPI Dependency for Database Session
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
