from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import NullPool

from app import config

database_url = (
    f"postgresql+asyncpg://{config.POSTGRES_USER}:{config.POSTGRES_PASSWORD}"
    f"@{config.POSTGRES_HOST}:{config.POSTGRES_PORT}/{config.POSTGRES_DB}"
)


engine = create_async_engine(
    database_url,
    echo=True,
    poolclass=NullPool,
)

async_session = sessionmaker(engine, expire_on_commit=False, class_=AsyncSession)
