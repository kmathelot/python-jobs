"""
GitHub command
"""
import logging
from datetime import date, timedelta, datetime

import requests

from sqlalchemy.orm import sessionmaker

from config import Config, Base
from core.interfaces.abs_command import AbsCommand
from core.models.workflows import Workflow
from core.models.repositories import Repository
from core.models.workflows_run import WorkflowRun


class GithubException(Exception):
    """Custom Gihutb Exception"""


class Github(AbsCommand):
    """GitHub import"""

    name = "github"
    logger = logging.getLogger(f"{AbsCommand.NAMESPACE}/{name}")

    session_maker = None
    session = None

    target_date = None

    def run(self, **kwargs):
        """Entrypoint
        date -- date iso format for data fetching. Default is yesterday
        todo : add date option and runs selection (repos, workflows, actions, times)
        """
        self.logger.info("hello from %s", self.name)

        self.target_date = kwargs.get('args').date

        # Update repo table
        self.logger.info("Getting repositories")
        for repos_list in self.get_repositories_from_api():
            self.__upsert(repos_list, Repository, ['updated_at', 'pushed_at'])

        # Deactivate or active repositories based on the last push
        self.toggle_active()

        # Update repo related
        for repos in self.session.query(Repository).filter(Repository.active == True).all():
            # Update Workflows
            self.upsert_workflows(repos)

            # Update actions
            self.upsert_workflows_run(repos)

    def build_context(self, config: Config):
        """Add the config values to the class and build a db session
        config -- Config object. Needs to have db attributes
        """
        self.config = config
        self.session_maker = sessionmaker(bind=config.db_engine)
        self.session = self.session_maker()

    def toggle_active(self):
        """Mark inactive all repos where the last push is > than 3 month"""
        compared_date = datetime.today() - timedelta(days=90)
        for repos in self.session.query(Repository).all():
            if repos.pushed_at < compared_date:
                repos.active = False
            else:
                repos.active = True
        self.session.commit()

    def upsert_repositories(self, repositories_list: [Repository]):
        """Update repositories table with new values"""
        self.__upsert(repositories_list, Repository)

    def upsert_workflows(self, repository: Repository):
        """Update a workflow if it exists, insert if not"""
        workflow_api_list = self.get_repository_workflows_from_api(repos_name=repository.name)

        if len(workflow_api_list) > 0:
            wkfl_list = map(lambda x: x.set_repos(repository.id), workflow_api_list)
            self.__upsert(list(wkfl_list), Workflow)

        self.logger.debug("No Workflows with %s", repository.name)

    def upsert_workflows_run(self, repository: Repository):
        """Update a workflow run if it exists, insert if not"""
        workflow_runs_api_list = self.get_repository_actions_from_api(repos_name=repository.name)

        if len(workflow_runs_api_list) > 0:
            run_list = map(self.__add_run_values, workflow_runs_api_list)
            self.__upsert(list(run_list), WorkflowRun)
        self.logger.debug("No runs with %s", repository.name)

    def get_repositories_from_api(self) -> [Repository]:
        """Get repositories from GH API"""
        page = 1

        while True:
            repos_data = self.get(f"{self.config.gh_url}/orgs/<orga>/repos", query_params={'page': page, 'sort': 'updated', 'per_page': 50})

            if len(repos_data) == 0:
                break

            yield [Repository.from_json(repo) for repo in repos_data]
            page += 1

    def get_repository_actions_from_api(self, repos_name: str) -> [dict]:
        """Get actions from a repos"""
        try:
            actions_data = self.get(f"{self.config.gh_url}/repos/<orga>/{repos_name}/actions/runs", {'created': self.target_date})
            return [WorkflowRun.from_json(action) for action in actions_data.get('workflow_runs')]
        except GithubException:
            return []

    def get_repository_workflows_from_api(self, repos_name: str) -> [Workflow]:
        """Get workflows from GH API"""
        self.logger.info("Getting workflows for %s", repos_name)
        try:
            workflows_data = self.get(f"{self.config.gh_url}/repos/<orga>/{repos_name}/actions/workflows")
            return [Workflow.from_json(wklf) for wklf in workflows_data.get('workflows')]
        except GithubException:
            return []

    def get(self, url, query_params=None):
        """Http get generic function. No needs to be in this class"""
        if query_params is None:
            query_params = {}
        query = requests.get(url=url, headers=self.__get_headers(), timeout=15, params=query_params)

        if query.status_code == 200:
            return query.json()
        else:
            self.logger.error("Error with url : %s, code %s", query.url, query.status_code)
            raise GithubException(f"Error when contacting api {query.url}, error code : {query.status_code}")

    def __get_headers(self):
        """Return GitHub API dedicated header for auth"""
        return dict(
            Accept='application/vnd.github+json',
            Authorization=f"Bearer {self.config.gh_token}",
        )

    def __upsert(self, data_list, model: Base, update_attrs=None):

        if update_attrs is None:
            update_attrs = ['updated_at']

        self.logger.debug("%i element typed %s to evaluate", len(data_list), model.__tablename__)
        for v in data_list:
            self.logger.info(v)
            row = self.session.get(model, v.id)
            if row is not None:  # update attributes if row already exists
                for attr in update_attrs:
                    setattr(row, attr, getattr(v, attr))
            else:
                self.session.add(v)
        self.session.commit()

    def __add_run_values(self, run: WorkflowRun) -> WorkflowRun:
        # prepare
        run.set_ids()

        # get usage
        usage = self.get(f"{self.config.gh_url}/repos/<orga>/{run.repository.get('name')}/actions/runs/{run.id}/timing")

        run.run_duration_ms = usage.get('run_duration_ms')

        if usage['billable'].get('UBUNTU') is not None:
            run.billable_usage = usage['billable']['UBUNTU']['total_ms']

        return run
