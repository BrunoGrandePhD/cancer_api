#!/usr/bin/env python

from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from base import Base


Session = sessionmaker()


class DatabaseConnection(object):
    """Base class for database connections"""

    def start_session(self):
        """Instantiate session instance and return it"""
        Session.configure(bind=self.engine)
        self.session = Session()
        return self.session

    def close_session(self):
        """Close session instance"""
        self.session.close()

    def create_tables(self):
        """Creates all tables according to base"""
        Base.metadata.create_all(self.engine)

    def drop_tables(self):
        """Creates all tables according to base"""
        Base.metadata.drop_all(self.engine)

    def __enter__(self):
        """Starts session and returns it for with statements"""
        return self.start_session()

    def __exit__(self):
        """Closes session on exit of with statement"""
        return self.close_session()


class MysqlConnection(DatabaseConnection):
    """Class for connecting to a MySQL database"""

    def __init__(self, host="localhost", user=None, password="",
                 database=None, port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.engine = create_engine(
            "mysql+pymysql://{user}:{password}@{host}:{port}/{database}".format(**vars(self)))


class SqliteConnection(DatabaseConnection):
    """Class for connecting to a SQLite database"""

    def __init__(self, filepath=""):
        self.filepath = filepath
        if self.filepath == "":
            # In-memory database
            self.engine = create_engine("sqlite://")
        else:
            # File database
            self.engine = create_engine("sqlite:///{filepath}".format(**vars(self)))
