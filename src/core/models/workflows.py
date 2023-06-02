from sqlalchemy import Table, Column, Integer, String, ForeignKey, BigInteger
from sqlalchemy.orm import registry, relationship
from core.interfaces.base_model import BaseModel
from core.models.workflows_run import WorkflowRun
from config import Base

mapper_registry = registry()


class Workflow(Base, BaseModel):

    __tablename__ = "workflows"

    id: int = Column(BigInteger, primary_key=True)
    name: str = Column(String)
    state: str = Column(String)
    created_at: str = Column(String)
    updated_at: str = Column(String)
    repository_id: int = Column(BigInteger, ForeignKey("repositories.id"))

    def set_repos(self, repos_id):
        self.repository_id = repos_id
        return self

    def __repr__(self):
        rep = f"Workflow({self.id},{self.name},{self.state},{self.repository_id})"
        return rep

