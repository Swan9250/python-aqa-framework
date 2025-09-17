import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")
DB_CREDS = f"{DB_USER}:{DB_PASSWORD}"
DB_HOST = os.getenv("DB_HOST")
DB_PORT = os.getenv("DB_PORT")
DB_ADDRESS = f"{DB_HOST}:{DB_PORT}"
DB_NAME = os.getenv("DB_NAME")

DB_URI = f"mysql://{DB_CREDS}@{DB_ADDRESS}/{DB_NAME}"

engine = create_engine(
    DB_URI,
    pool_size=5,
    max_overflow=10,
    pool_timeout=30,
    pool_recycle=1800,
    echo=False,
)

SessionLocal = sessionmaker(bind=engine, autocommit=False, autoflush=False)
ScopedSession = scoped_session(SessionLocal)
