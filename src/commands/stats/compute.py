"""
Compute stats
"""
import logging
import re

from collections import namedtuple

import sqlparse

from sqlalchemy import and_, func
from sqlalchemy.orm import sessionmaker

from config import Config
from core.interfaces.abs_command import AbsCommand
from core.models.rds_log_entries import RdsLogEntries
from core.models.rds_sql_stats import RdsSqlStats


class Compute(AbsCommand):
    """Compute stats"""

    name = "compute"
    logger = logging.getLogger(f"{AbsCommand.NAMESPACE}/{name}")

    def run(self, **kwargs):
        self.logger.info("hello from %s", self.name)

        target_date = kwargs.get('args').date

        results = self.session.query(RdsLogEntries).filter(
            and_(RdsLogEntries.log_type == "LOG", func.date(RdsLogEntries.timestamp) == target_date)).all()

        for query_obj in results:
            row = self.session.get(RdsSqlStats, query_obj.id)
            if not row:
                parsed_values = self.__parse_query(query_obj.log_value)
                self.logger.info(f"${query_obj.id}:${query_obj.integrity} - ${parsed_values}")

                query_stats = RdsSqlStats.create_from_log_entry(query_obj)
                query_stats.set_stats(*parsed_values)
                query_stats.parameters = self.__get_parameters(query_obj.process_id)
                self.session.add(query_stats)

        self.session.commit()

    def build_context(self, config: Config):
        """Add the config values to the class and build a db session
        config -- Config object. Needs to have db attributes
        """
        self.config = config
        self.session_maker = sessionmaker(bind=config.db_engine)
        self.session = self.session_maker()

    def __parse_query(self, query: str):
        """Can be moved to utils"""
        parsed_query = sqlparse.parse(query)[0]
        tokens = parsed_query.tokens

        SqlStats = namedtuple("SqlStats", "query_schema query_table table_join")

        table_name = ''
        schema_name = ''
        joins = 0

        for token in parsed_query.tokens:
            if token.value.lower() == 'from' and table_name == '':

                index = 1

                # get the next index with data after from
                for i in range(1, len(tokens)):
                    if not tokens[tokens.index(token) + i].is_whitespace:
                        index = i
                        break

                # particular nested query case
                if 'from' in tokens[tokens.index(token) + index].value.lower():
                    return self.__parse_query(tokens[tokens.index(token) + index].value[1:])

                # It is still possible that we can't split the values
                try:
                    raw_value = tokens[tokens.index(token) + index].value.split(" ")[0]
                except ValueError:
                    raw_value = "undefined.undefined"

                try:
                    schema_name, table_name = re.search(r"\W?(\w+.\w+)\W?\.\W?(\w+.\w+)\W?", raw_value).groups()
                except AttributeError:
                    self.logger.error("Error : {}".format(raw_value))

            elif token.value.lower() in ['left join', 'inner join', 'right join', 'full join']:
                joins = joins + 1

        return SqlStats(schema_name, table_name, joins)

    def __get_parameters(self, process_id):
        rows: list[RdsLogEntries] = self.session.query(RdsLogEntries).filter(
            and_(RdsLogEntries.process_id == process_id, RdsLogEntries.log_type == 'DETAIL')).limit(1).all()

        if len(rows) == 0:
            return 0

        if rows[0]:
            params_group = re.findall(r"\$\d", rows[0].log_value)
            return len(params_group)
