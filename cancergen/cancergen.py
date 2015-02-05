#!/usr/bin/env python

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from exceptions import *


class BaseMixin(object):
    """Provides methods to Base"""

    @classmethod
    def get_or_create(cls, session, **kwargs):
        """If a model's unique_on class attribute is defined,
        get_or_create will first search the database for an
        existing instance based on the attributes listed in
        unique_on. Otherwise, it will create an instance.
        Note that the session still needs to be committed.
        """
        # Check if class' unique_on is defined
        try:
            cls.unique_on
        except AttributeError:
            raise UndefinedUniqueOnError("The {} class doesn't have a defined unique_on "
                                         "class attribute.".format(cls.__name__))
        # Create subset of kwargs according to unique_on
        unique_kwargs = {k: v for k, v in kwargs.iteritems() if k in cls.unique_on}
        # Check if instance already exists based on unique_kwargs
        count = session.query(cls).filter_by(**unique_kwargs).count()
        if count > 1:
            # Ambiguous unique instances
            raise MultipleUniqueInstancesError(
                "More than one instance returned when looking for unique instance.")
        elif count == 1:
            # Instance already exists; obtain it and return it
            instance = session.query(cls).filter_by(**unique_kwargs).first()
        elif count == 0:
            # Instance doesn't already exist, so create a new one
            instance = cls(**kwargs)
            session.add(instance)
        return instance


Base = declarative_base(cls=BaseMixin)


Session = sessionmaker()


class CancerGenDB(object):
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

    def __exit__(self, type, value, traceback):
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
