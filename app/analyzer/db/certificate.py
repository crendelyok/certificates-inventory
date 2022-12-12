from ipaddress import IPv4Address

from sqlalchemy import Boolean, Column, DateTime, Integer, Text, select

from app.common.database.db_setup import DBSetup


class FoundCertificate(DBSetup.Base):
    __tablename__ = "found_certificate"

    rowid = Column(Integer, nullable=False, primary_key=True, autoincrement=True)
    bcert = Column(Text, nullable=False)
    version = Column(Text, nullable=False)
    issuer = Column(Text, nullable=False)
    notBefore = Column(DateTime, nullable=False)
    notAfter = Column(DateTime, nullable=False)
    PublicKeyLen = Column(Integer, nullable=False)
    PublicKeyAlg = Column(Text, nullable=False)
    SignatureAlg = Column(Text, nullable=False)
    HashAlg = Column(Text, nullable=False)
    issuerError = Column(Boolean, nullable=False)

    ip = Column(Text, nullable=False)
    port = Column(Integer, nullable=False)

    queryId = Column(Integer, nullable=False)

    def __repr__(self) -> str:
        return (f"<FoundCertificate(version='{self.version}', issuer='{self.issuer}', "
                f"notBefore='{self.notBefore}'), notBefore='{self.notBefore}', "
                f"notAfter='{self.notAfter}', PublicKeyLen='{self.PublicKeyLen}', "
                f"PublicKeyAlg='{self.PublicKeyAlg}', SignatureAlg='{self.SignatureAlg}', "
                f"HashAlg='{self.HashAlg}', issuerError='{self.issuerError}', "
                f"ip='{self.ip}', port='{self.port}', queryId='{self.queryId}'>")

    def to_json(self) -> dict:
        res = {
            key: (value if not isinstance(value, str) else value.strip("_"))
            for key, value in vars(self).items()
            if not key.startswith("_")
        }
        del res["bcert"]
        del res["rowid"]
        return res

    async def insert(self):
        async with DBSetup.Session.begin() as session:
            if isinstance(self.bcert, bytes):
                self.bcert = str(self.bcert)
            if isinstance(self.ip, IPv4Address):
                self.ip = str(self.ip)
            session.add(self)

    @staticmethod
    async def get_by_query_id(query_id: int) -> list:
        async with DBSetup.Session() as session:
            stmt = select(FoundCertificate).where(FoundCertificate.queryId == query_id)
            cursor = await session.execute(stmt)
            return cursor.scalars().fetchall()
