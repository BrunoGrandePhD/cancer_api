"""
__init__.py
===========
Where it all begins.
"""

__version__ = "0.1.4"

from main import connect, get_connection, set_connection
from connections import MysqlConnection, SqliteConnection
from mutations import SingleNucleotideVariant, Indel, CopyNumberVariation, StructuralVariation
from metadata import Patient, Sample, Library
from annotations import Gene, Transcript, Exon, Protein
import files
import parsers
import utils
