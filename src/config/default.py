"""
Default config values
"""
import os

default_config = dict(
  db_host=os.getenv('DB_HOST'),
  db_user=os.getenv('DB_USER'),
  db_pass=os.getenv('DB_PASS'),
  db_port=os.getenv('DB_PORT'),
  db_name=os.getenv('DB_NAME'),
  gh_url='https://api.github.com',
  gh_token=os.getenv('GH_TOKEN')
)
