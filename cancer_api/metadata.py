"""
metadata.py
===========
This submodule contains all classes representing metadata
entities, such as patients, samples and derived DNA libraries.
"""

from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from base import Base


class Patient(Base):
    """Model for patients"""

    id = Column(Integer, primary_key=True)
    patient_name = Column(String(length=100))


class Sample(Base):
    """Model for samples"""

    id = Column(Integer, primary_key=True)
    sample_name = Column(String(length=100))
    sample_type = Column(Enum("normal", "primary", "metastasis", "relapse"))
    patient_id = Column(Integer, ForeignKey("patient.id"))


class Library(Base):
    """Model for libraries"""

    id = Column(Integer, primary_key=True)
    library_name = Column(String(length=100))
    library_type = Column(Enum("genome", "exome", "rnaseq", "mirnaseq", "targeted"))
    sample_id = Column(Integer, ForeignKey("sample.id"))
