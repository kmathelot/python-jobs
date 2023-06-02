"""
Init Db
"""
import logging
import re
import os

from sqlalchemy.orm import sessionmaker

from config import Config, Base
from core.interfaces.abs_command import AbsCommand
from core.models.rds_log_files import RdsLogFiles
from core.models.rds_log_entries import RdsLogEntries


class Aws(AbsCommand):
    """AWS fetcher"""

    name = "aws"
    logger = logging.getLogger(f"{AbsCommand.NAMESPACE}/{name}")

    target_date = None
    path_file = None

    def run(self, **kwargs):
        """Command entry point"""
        self.logger.info("hello from %s", self.name)

        self.target_date = kwargs.get('args').date

        # in fact this file name doesn't really matter.
        path_file = f"/tmp/{self.target_date}.txt"

        # Clean in case of residual execution
        self.__clean_local_file(path_file)

        # get the log list based on the date and keep only unprocessed
        log_file_list = filter(lambda file: file.processed == False, list(map(self.save_log_list, self.get_log_list())))

        with open(path_file, 'a+') as file_handler:

            # parse only files that have not already been parsed
            for file in log_file_list:
                # Download file and write it to the fs
                self.download_log_file(file, file_handler)
                file.toggle_processed()

            # rewind
            file_handler.seek(0)

            for raw_log_entry in self.__aggregate_log_lines(file_handler):
                entry = RdsLogEntries.create_from_raw(raw_log_entry)
                if entry:
                    self.session.add(entry)

            self.session.commit()

        self.__clean_local_file(path_file)

        self.logger.info("Done")

    def build_context(self, config: Config):
        """Add the config values to the class and build a db session
        config -- Config object. Needs to have db attributes
        """
        self.config = config
        self.session_maker = sessionmaker(bind=config.db_engine)
        self.session = self.session_maker()

    def save_log_list(self, log_file: RdsLogFiles) -> RdsLogFiles:
        """Check if log file has already been downloaded"""
        row: RdsLogFiles = self.session.query(RdsLogFiles).filter(RdsLogFiles.LogFileName == log_file.LogFileName).one_or_none()

        if row is not None:
            return row
        else:
            self.session.add(log_file)
            self.session.commit()
            return log_file

    def get_log_list(self) -> [RdsLogFiles]:
        """Get logs files names"""
        client = self.config.get_aws_client('rds')

        log_files = []
        marker = ''

        while marker is not None:
            response = client.describe_db_log_files(
                DBInstanceIdentifier='<dbhost>',
                MaxRecords=50,
                FilenameContains=f"{self.target_date}",
                Marker=marker
            )

            log_files.extend(response['DescribeDBLogFiles'])

            if not response.get('Marker'):
                marker = None
            else:
                marker = response.get('Marker')

        return [RdsLogFiles.from_json(log) for log in log_files]

    def download_log_file(self, file_name, file_handler):
        """File download. It's easier to write the file and after check every line of log
        It helps to handle newlines in sql queries"""
        client = self.config.get_aws_client('rds')

        pending_data = True
        marker = '0'

        while pending_data is True:
            self.logger.info(f"Trying to download {file_name.LogFileName}")
            log = client.download_db_log_file_portion(
                DBInstanceIdentifier='<dbhost>',
                LogFileName=file_name.LogFileName,
                Marker=marker
            )

            file_handler.write(log['LogFileData'])

            self.logger.info(f"data marker is {log.get('Marker')}")
            pending_data = log.get('AdditionalDataPending')
            marker = log.get('Marker')

    def save_log_entry(self, log_entry):
        pass
    def __aggregate_log_lines(self, file_obj):
        """It's fairly possible to move it into the utils file"""
        full_line = []

        date_pattern = r"^\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\sUTC"

        while True:
            line = file_obj.readline()

            if not line:
                # but yield in case of there is lines
                if len(full_line) > 0:
                    yield " ".join(full_line)
                    full_line = []
                break

            if re.match(date_pattern, line): # Line starts with a date -> Yield previous
                yield " ".join(full_line)
                full_line = [line]
            else:
                full_line.append(line)

    def __clean_local_file(self, path):
        if os.path.exists(path):
            os.remove(path)