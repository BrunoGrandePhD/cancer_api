"""
__init__.py
===========
Where it all begins.
"""

from main import connect, get_connection, set_connection
from connections import MysqlConnection, SqliteConnection
from mutations import SingleNucleotideVariant, Indel, CopyNumberVariation, StructuralVariation
from metadata import Patient, Sample, Library
from annotations import Gene, Transcript, Exon, Protein
from files import *
from parsers import *
from utils import *

__version__ = "0.2.0"
