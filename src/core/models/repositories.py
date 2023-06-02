from sqlalchemy import Column, String, BigInteger, Boolean, DateTime
from sqlalchemy.orm import relationship

from core.interfaces.base_model import BaseModel
from core.models.workflows import Workflow
from config import Base


class Repository(Base, BaseModel):

    __tablename__ = "repositories"

    id: int = Column(BigInteger, primary_key=True)
    name: str = Column(String)
    full_name: str = Column(String)
    description: str = Column(String)
    updated_at: str = Column(DateTime)
    pushed_at: str = Column(DateTime)
    active: bool = Column(Boolean, nullable=False, default=True)
    workflow: int = relationship("Workflow")

    def __repr__(self):
        rep = f"Repository({self.id},{self.name})"
        return rep
