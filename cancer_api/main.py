"""
main.py
=======
This submodule contains classes and functions that serve
to maintain the database connection and session.
"""

from sqlalchemy.orm import sessionmaker
from exceptions import IllegalVariableDefinition, NotConnectedToDatabase


Session = sessionmaker()


class App(object):
    """Class for storing all variables for current 'session'."""
    def __init__(self):
        super(App, self).__init__()

    @property
    def connection(self):
        try:
            self._connection
        except AttributeError:
            raise NotConnectedToDatabase("Database connection needed. "
                                         "See `cancer_api.connect` function")
        return self._connection

    @connection.setter
    def connection(self, value):
        self._connection = value

    def connect(self, database_connection):
        """Bind a database connection to current 'session'."""
        self.connection = database_connection
        Session.configure(bind=database_connection.engine)
        session = Session()
        self.connection.session = session
        return self.connection

    @property
    def session(self):
        return self.connection.session

    @session.setter
    def session(self, value):
        raise IllegalVariableDefinition("Please define the `session` by connecting to a "
                                        "database using the `cancer_api.connect` function.")


# Instantiate an instance of the App class, which will store
# all variables relating to this 'session' (i.e. package import)
app = App()


# Have some user-facing functions that operate on the app instance
def set_connection(database_connection):
    """app.connection setter"""
    return app.connect(database_connection)


def get_connection():
    """app.connection getter"""
    return app.connection


def connect(database_connection):
    """Proxy for app.connect()"""
    return set_connection(database_connection)
