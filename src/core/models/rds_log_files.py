from sqlalchemy import Column, String, BigInteger, Boolean, DateTime

from core.interfaces.base_model import BaseModel
from config import Base


class RdsLogFiles(Base, BaseModel):

    __tablename__ = "rds_log_files"

    id: int = Column(BigInteger, primary_key=True, autoincrement=True)
    LogFileName: str = Column(String, unique=True)
    processed: bool = Column(Boolean, nullable=False, default=False)

    def toggle_processed(self):
        self.processed = not self.processed

    def __repr__(self):
        rep = f"log_file({self.id},{self.LogFileName})"
        return rep
