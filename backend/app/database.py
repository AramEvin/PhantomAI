from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column
from sqlalchemy import String, Integer, Float, DateTime, JSON
from datetime import datetime, timezone
from app.core.config import settings

engine = create_async_engine(settings.DATABASE_URL, echo=False, pool_size=10, max_overflow=20)
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

class Base(DeclarativeBase):
    pass

class ScanRecord(Base):
    __tablename__ = "scans"
    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    target: Mapped[str] = mapped_column(String(255), index=True)
    target_type: Mapped[str] = mapped_column(String(10))
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    duration_ms: Mapped[float] = mapped_column(Float)
    tools_run: Mapped[int] = mapped_column(Integer)
    tools_success: Mapped[int] = mapped_column(Integer)
    risk_level: Mapped[str] = mapped_column(String(20), nullable=True)
    risk_score: Mapped[int] = mapped_column(Integer, nullable=True)
    results: Mapped[dict] = mapped_column(JSON, nullable=True)
    ai_analysis: Mapped[dict] = mapped_column(JSON, nullable=True)

async def init_db():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
