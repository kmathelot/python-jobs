from sqlalchemy import Column, String, BigInteger, DECIMAL, DateTime, Integer

from core.interfaces.base_model import BaseModel
from core.models.rds_log_entries import RdsLogEntries
from config import Base


class RdsSqlStats(Base, BaseModel):

    __tablename__ = "rds_sql_stats"

    id: str = Column(BigInteger, primary_key=True,)
    timestamp: str = Column(DateTime, nullable=False)
    user: str = Column(String, nullable=False)
    query_schema: str = Column(String, nullable=False)
    query_table: str = Column(String, nullable=False)
    duration: float = Column(DECIMAL, default=0)
    parameters: int = Column(Integer, default=0)
    join_table: int = Column(Integer, default=0)

    @classmethod
    def create_from_log_entry(cls, logEntry: RdsLogEntries):
        return cls(
            id=logEntry.id,
            timestamp=logEntry.timestamp,
            user=logEntry.user,
            duration=logEntry.duration,
        )

    def set_stats(self, schema: str, table: str, joins=0):
        self.query_schema = schema
        self.query_table = table
        self.join_table = joins

    def has_stats(self):
        return self.query_table != '' and self.query_schema != ''

    def __repr__(self):
        rep = f"query_stat(schema: ${self.query_schema}, table : ${self.query_table}, joins: ${self.join_table})"
        return rep
