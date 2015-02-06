__version__ = "0.1"

from connections import MysqlConnection, SqliteConnection
from mutations import SingleNucleotideVariant, CopyNumberVariation, StructuralVariation
from metadata import Patient, Sample, Library
from annotations import Gene, Transcript, Exon, Protein
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
