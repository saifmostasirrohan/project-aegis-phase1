from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.orm import declarative_base

# The local SQLite file
DATABASE_URL = "sqlite+aiosqlite:///./aegis_memory.db"

# Create the async engine
engine = create_async_engine(DATABASE_URL, echo=False)

# Session factory
AsyncSessionLocal = async_sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

Base = declarative_base()


# Dependency to inject DB sessions into FastAPI routes
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session
