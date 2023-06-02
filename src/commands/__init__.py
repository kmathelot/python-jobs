"""Command entrypoint"""
from typing import Dict

from commands.db.clean import Clean
from commands.db.init import Init
from commands.fetch.github import Github
from commands.fetch.aws import Aws
from commands.stats.compute import Compute

from core.interfaces.abs_command import AbsCommand

db_commands = dict((cls.name, cls) for cls in (Clean, Init))

fetch_commands = dict((cls.name, cls) for cls in (Github, Aws))

stats_commands = dict((cls.name, cls) for cls in (Compute,))

all_commands = dict(db_commands, **fetch_commands, **stats_commands)


def parse_command(action: str) -> AbsCommand:
    """
    Get the right command
    :param action:
    :return: Command interface
    """
    command = all_commands.get(action)
    return command()
