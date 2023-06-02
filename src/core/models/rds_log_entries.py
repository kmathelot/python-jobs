import re
import hashlib
from sqlalchemy import Column, String, BigInteger, Integer, DateTime, Text, DECIMAL

from core.interfaces.base_model import BaseModel
from config import Base


class RdsLogEntries(Base, BaseModel):

    __tablename__ = "rds_log_entries"

    id: int = Column(BigInteger, primary_key=True, autoincrement=True)
    timestamp: str = Column(DateTime, nullable=False)
    ip_address: str = Column(String, nullable=False)
    user: str = Column(String, nullable=False)
    process_id: str = Column(Integer, nullable=False)
    log_type: str = Column(String, nullable=False)
    duration: float = Column(DECIMAL, default=0)
    log_value: str = Column(Text, nullable=False)
    integrity: str = Column(String, nullable=False)

    @classmethod
    def create_from_raw(cls, raw_values):
        #
        log_pattern = r"^(\d{4}-\d{2}-\d{2}\s\d{2}:\d{2}:\d{2}\sUTC):((?:[0-9]{1,3}\.){3}[0-9]{1,3})\(\d+\):(\w+\@\w+):\[(\d+)\]:(\w+):\s{2}(\w+):\s(\d*\.*\d*).*"

        # try to match
        values = re.match(log_pattern, raw_values)

        if not values:
            return None

        # sanitize some values
        duration = 0

        # Index for selecting the end of the log entry
        index = raw_values.index(values.group(6))

        if values.group(6) == "duration":
            # Find the first occurrence of the SQL command
            query_command = re.search(r"(SELECT|INSERT|UPDATE|TRUNCATE|DELETE|COMMIT|ROLLBACK)", raw_values, re.IGNORECASE)
            if query_command:
                index = raw_values.index(query_command.group(1))
                if values.group(7) is not '':
                    duration = values.group(7) 

        log_value = raw_values[index:-1]

        return cls(timestamp=values.group(1),
                   ip_address=values.group(2),
                   user=values.group(3),
                   process_id=values.group(4),
                   log_type=values.group(5),
                   duration=duration,
                   log_value=log_value,
                   integrity=hashlib.md5(log_value.encode("utf-8")).hexdigest()
                   )

    def __repr__(self):
        rep = f"log_entry({self.id},{self.timestamp},{self.user})"
        return rep
