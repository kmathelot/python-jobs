import json

from sqlalchemy import Table, Column, Integer, String, ForeignKey, BigInteger, DateTime
from sqlalchemy.orm import registry, relationship
from core.interfaces.base_model import BaseModel
from config import Base

mapper_registry = registry()


class WorkflowRun(Base, BaseModel):

    __tablename__ = "workflows_run"

    id: int = Column(BigInteger, primary_key=True)
    name: str = Column(String)
    status: str = Column(String)
    event: str = Column(String)
    conclusion: str = Column(String, nullable=False)
    created_at: str = Column(DateTime)
    updated_at: str = Column(DateTime)
    run_started_at: str = Column(DateTime)
    run_attempt: int = Column(Integer)
    actor_type: str = Column(String)
    workflow_id: int = Column(BigInteger)
    repository_id: int = Column(BigInteger, ForeignKey("repositories.id"))
    billable_usage: int = Column(Integer, nullable=False, default=0)
    run_duration_ms: int = Column(BigInteger, nullable=False, default=0)

    repository: dict = {}
    actor: dict = {}

    def set_ids(self):
        self.repository_id = self.repository.get('id')
        self.actor_type = self.actor.get('type')

        if not self.conclusion:
            self.conclusion = "undefined"

        return self

    def __repr__(self):
        rep = f"WorkflowRun({self.id},{self.name},{self.status},{self.conclusion},{self.repository_id})"
        return rep

