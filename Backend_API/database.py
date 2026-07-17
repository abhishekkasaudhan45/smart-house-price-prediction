"""Database configuration and session management."""

import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, DeclarativeBase

DATABASE_URL = os.environ.get(
    "DATABASE_URL",
    (  # Render PostgreSQL URL
        "postgresql://house_user:sqe0NJk4HdbAueLBnjbqiAbv1MxlW7pB"
        "@dpg-d9a9lf7aqgkc739af87g-a/house_prices_0qgv"
    ),
)

# Render provides postgres:// but SQLAlchemy needs postgresql://
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql://", 1)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


class Base(DeclarativeBase):
    pass


def get_db():
    """Yield a database session and close it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Create all tables. Safe to call multiple times.

    If the predictions table exists with the old (pre-Bengaluru) schema,
    drop and recreate it — history is demo data, mirroring migration 0002.
    """
    from sqlalchemy import inspect

    inspector = inspect(engine)
    if "predictions" in inspector.get_table_names():
        cols = {c["name"] for c in inspector.get_columns("predictions")}
        if "total_sqft" not in cols:
            Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
