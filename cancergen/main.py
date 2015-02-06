#!/usr/bin/env python

from sqlalchemy.orm import sessionmaker
from connections import DatabaseConnection


Session = sessionmaker()


connection = DatabaseConnection()


def connect(db_cnx):
    """Conveniently establishes a database connection"""
    global connection  # Edit module connection variable
    Session.configure(bind=db_cnx.engine)
    session = Session()
    db_cnx.session = session
    connection = db_cnx
    return connection
