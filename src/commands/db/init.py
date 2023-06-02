"""
Init Db
"""
import logging

from sqlalchemy.orm import sessionmaker

from config import Config, Base
from core.interfaces.abs_command import AbsCommand
from core.models.workflows import Workflow
from core.models.repositories import Repository
from core.models.workflows_run import WorkflowRun
from core.models.rds_log_files import RdsLogFiles
from core.models.rds_sql_stats import RdsSqlStats



class Init(AbsCommand):
    """Database init"""

    name = "init"
    logger = logging.getLogger(f"{AbsCommand.NAMESPACE}/{name}")

    def run(self, **kwargs):
        """Command entry point"""
        self.logger.info("hello from %s", self.name)

        self.logger.info("Database init")
        Base.metadata.create_all(self.config.db_engine)
        self.logger.info("Done")

    def build_context(self, config: Config):
        """Add the config values to the class and build a db session
        config -- Config object. Needs to have db attributes
        """
        self.config = config
        self.session_maker = sessionmaker(bind=config.db_engine)
        self.session = self.session_maker()
