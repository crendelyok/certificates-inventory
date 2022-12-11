from sqlalchemy import Column, Integer, Text, select, DateTime

from app.common.utils.db_setup import DBSetup


class FoundUser(DBSetup.Base):
    __tablename__ = "found_user"

    rowid = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    # TODO(dslynko): check whether these info is needed
    start_time = Column(DateTime, nullable = False) # when cert was given
    expiry_time = Column(DateTime, nullable = False) # expiry date
    keylen = Column(Integer, nullable = False)
    algo_signature = Column(Text, nullable = False)
    algo_cipher = Column(Text, nullable = False)

    async def insert(self):
        async with DBSetup.Session.begin() as session:
            session.add(self)

    @staticmethod
    async def get_by_id(user_id: int):
        async with DBSetup.Session() as session:
            cursor = await session.execute(select(FoundUser).where(FoundUser.rowid == user_id))
            return cursor.scalar()

    @staticmethod
    async def get_all():
        async with DBSetup.Session() as session:
            cursor = await session.execute(select(FoundUser))
            return cursor.scalars().fetchall()
