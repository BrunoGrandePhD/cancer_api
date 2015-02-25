"""
connections.py
==============
This submodule contains classes representing database
connections, used in the main submodule.
"""

from sqlalchemy import create_engine
from base import Base
from exceptions import NotConnectedToDatabase


class DatabaseConnection(object):
    """Base class for database connections"""

    def __init__(self, url=None):
        if url:
            self.engine = create_engine(url)

    @property
    def session(self):
        try:
            self._session
        except AttributeError:
            raise NotConnectedToDatabase("Database connection needed. "
                                         "See `cancer_api.connect` function")
        return self._session

    @session.setter
    def session(self, value):
        self._session = value

    @session.deleter
    def session(self):
        self.close()
        del self._session

    def close(self):
        """Close database connection"""
        self._session.close()

    def commit(self):
        """Commit the pending transaction"""
        self.session.commit()

    def create_tables(self):
        """Creates all tables according to base"""
        Base.metadata.create_all(self.engine)

    def drop_tables(self):
        """Creates all tables according to base"""
        Base.metadata.drop_all(self.engine)

    def __repr__(self):
        return str(vars(self))

    def __str__(self):
        return str(vars(self))


class MysqlConnection(DatabaseConnection):
    """Class for connecting to a MySQL database"""

    def __init__(self, host="localhost", user=None, password="",
                 database=None, port=3306):
        self.host = host
        self.user = user
        self.password = password
        self.database = database
        self.port = port
        self.url = "mysql+pymysql://{user}:{password}@{host}:{port}/{database}".format(
            **vars(self))
        super(MysqlConnection, self).__init__(self.url)


class SqliteConnection(DatabaseConnection):
    """Class for connecting to a SQLite database"""

    def __init__(self, filepath=""):
        self.filepath = filepath
        if self.filepath == "":
            self.url = "sqlite://"  # In-memory database
        else:
            self.url = "sqlite:///{filepath}".format(**vars(self))
        super(SqliteConnection, self).__init__(self.url)
