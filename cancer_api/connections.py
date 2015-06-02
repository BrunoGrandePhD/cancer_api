"""
connections.py
==============
This submodule contains classes representing database
connections, used in the main submodule.
"""

from sqlalchemy import create_engine


class DatabaseConnection(object):
    """Base class for database connections"""

    def __init__(self, url):
        self.engine = create_engine(url)

    def __repr__(self):
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
