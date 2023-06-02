"""Config builder"""
import os
import json
import boto3

from dataclasses import dataclass
from sqlalchemy import create_engine, engine
from sqlalchemy.engine import Engine
from sqlalchemy.orm import declarative_base

from config.default import default_config

Base = declarative_base()


class ConfigException(Exception):
    """Custom config exception"""


@dataclass
class Config:
    """
    Config Object
    """
    db_host: str
    db_port: int
    db_name: str
    db_user: str
    db_pass: str
    gh_url: str
    gh_token: str

    @property
    def db_engine(self) -> Engine:
        """Create a SQLAlchemy Db engine"""
        return create_engine(engine.URL.create(**self.db_config))

    @property
    def db_config(self):
        """Shorthand for db engine creation"""
        return {
            'drivername': 'postgresql+psycopg2',
            'username': self.db_user,
            'password': self.db_pass,
            'host': self.db_host,
            'port': self.db_port,
            'database': self.db_name
        }

    def get_aws_client(self, api):
        """Create boto client"""  # todo: Add secret key and token
        return boto3.client(api)

    @classmethod
    def build_config(cls, config_file):
        """
        Raise exception when config file doesn't match config signature
        """
        if config_file != "default":
            default_config.update(
                json.load(open(f"{os.path.abspath(os.path.dirname(__file__))}/{config_file}.json",
                          encoding='utf-8'))
            )
        try:
            return cls(**default_config)
        except TypeError:
            raise ConfigException("Wrong config file")
