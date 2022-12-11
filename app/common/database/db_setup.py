from sqlalchemy.orm import declarative_base, sessionmaker
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


class DBSetup:
    Base = declarative_base()
    Session = None

    DBLocation: str | None = None
    __engine = None

    @classmethod
    async def init(cls, db_path: str, **kwargs):
        cls.DBLocation = db_path
        cls.__engine = create_async_engine(f"sqlite+aiosqlite:///{cls.DBLocation}")
        cls.Session = sessionmaker(cls.__engine, class_=AsyncSession, **kwargs)
        await cls._init_models()

    @classmethod
    async def _init_models(cls):
        async with cls.__engine.begin() as connection:
            await connection.run_sync(cls.Base.metadata.create_all)
