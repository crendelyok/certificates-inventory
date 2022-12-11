from sqlalchemy import Column, DateTime, Integer, JSON, select

from app.common.database.db_setup import DBSetup


class SearchQuery(DBSetup.Base):
    __tablename__ = "search_request"

    rowid = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    config = Column(JSON, nullable=False)
    time_created = Column(DateTime, nullable=False)

    async def insert(self) -> int:
        async with DBSetup.Session(expire_on_commit=False) as session:
            session.add(self)
            await session.commit()
            return self.rowid

    @staticmethod
    async def get_by_id(query_id: int):
        async with DBSetup.Session() as session:
            stmt = select(SearchQuery).where(SearchQuery.rowid == query_id)
            cursor = await session.execute(stmt)
            return cursor.scalar()

    @staticmethod
    async def get_all():
        async with DBSetup.Session() as session:
            cursor = await session.execute(select(SearchQuery))
            return cursor.scalars().fetchall()
