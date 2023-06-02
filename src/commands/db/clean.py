"""
clean datas
"""
import logging

from core.interfaces.abs_command import AbsCommand


class Clean(AbsCommand):
    """Database cleaner"""

    name = "clean"
    logger = logging.getLogger(f"{AbsCommand.NAMESPACE}/{name}")

    def run(self, **kwargs):
        self.logger.info("hello from %s", self.name)
        print(kwargs)

