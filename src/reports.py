'''Reports CLI'''
import argparse
import logging
import sys, os
from datetime import date, timedelta

from commands import db_commands, fetch_commands, stats_commands, parse_command
from config import Config

# Basic logger
logging.basicConfig(level=logging.INFO)

LOGGER = logging.getLogger('reports/main')

if __name__ == "__main__":
    parser = argparse.ArgumentParser(prog="CH SRE reports CLI",
                                     description="Get data from one service to store it into our dbs")

    # Common args
    parser.add_argument('--config', help="json config file", required=False, default="default")
    parser.add_argument('--date', help="reference date to import data. ISO format", required=False, default=date.today() - timedelta(days=1))

    # subparsers
    subparsers = parser.add_subparsers()
    basic_cmd_parser = subparsers.add_parser('db', help="db management")
    basic_cmd_parser.add_argument('action', choices=db_commands)

    fetch_cmd_parser = subparsers.add_parser('fetch', help="get data from a service")
    fetch_cmd_parser.add_argument('action', help="Choose the source", choices=fetch_commands)

    stats_cmd_parser = subparsers.add_parser('stats', help="stats calculation")
    stats_cmd_parser.add_argument('action', choices=stats_commands)

    args = parser.parse_args()

    # Main arg managed manually because of the subparsers
    if not hasattr(args, 'action'):
        parser.print_help()
        exit()

    LOGGER.info('Command : %s', args.action)

    # Find the command
    app_command = parse_command(args.action)

    # build cli configuration
    cli_config = Config.build_config(args.config)

    # Catch Exception if postgres is not available
    # Configure command
    LOGGER.info("Job beginning...")

    try:
        # Set up the context regarding the config
        app_command.build_context(cli_config)
        # Execute the command
        app_command.run(args=args)
    except Exception as ex:
        LOGGER.error("Error while executing command. %s", ex)
        exc_type, exc_obj, exc_tb = sys.exc_info()
        filename = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        LOGGER.error(exc_type, filename, exc_tb.tb_lineno)
    finally:
        LOGGER.info("End of command")
