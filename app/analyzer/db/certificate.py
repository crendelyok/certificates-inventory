from sqlalchemy import Column, DateTime, Integer, JSON, Text, select

from app.analyzer.db import DBSetup


class FoundCertificate(DBSetup.Base):
    __tablename__ = "found_certificate"

    rowid = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    certificate = Column(Text, nullable=False)
    query_id = Column(Integer, nullable=False)
    # ipv4 or ipv6
    ip_addr = Column(Text, nullable=False)
    port = Column(Integer, nullable=False)
    time_issued = Column(DateTime, nullable=False)
    time_found = Column(DateTime, nullable=False)
    extra_args = Column(JSON, nullable=False)

    async def insert(self):
        async with DBSetup.Session.begin() as session:
            session.add(self)

    @staticmethod
    async def get_by_query_id(query_id: int) -> list:
        async with DBSetup.Session() as session:
            stmt = select(FoundCertificate).where(FoundCertificate.query_id == query_id)
            cursor = await session.execute(stmt)
            return cursor.scalars().fetchall()
