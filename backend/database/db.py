"""Database — async SQLAlchemy (SQLite dev / PostgreSQL prod)"""
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase
from typing import AsyncGenerator
import os, logging

logger = logging.getLogger("lifelens.db")
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite+aiosqlite:///./lifelens.db")
if DATABASE_URL.startswith("postgres://"):
    DATABASE_URL = DATABASE_URL.replace("postgres://", "postgresql+asyncpg://", 1)

IS_SQLITE = "sqlite" in DATABASE_URL
kw = {"echo": False}
if IS_SQLITE: kw["connect_args"] = {"check_same_thread": False}
else: kw.update(pool_size=10, max_overflow=20, pool_pre_ping=True)

engine = create_async_engine(DATABASE_URL, **kw)
SessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

class Base(DeclarativeBase): pass

async def init_db():
    from models.user import User
    from models.patient import Patient
    from models.prediction import Prediction
    from models.report import Report
    from models.appointment import Appointment
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)
    logger.info("✅ DB tables ready")

async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with SessionLocal() as s:
        try: yield s; await s.commit()
        except: await s.rollback(); raise
