"""
mutations.py
============
This submodule contains all classes representing mutations
in cancer, notably SNVs, indels, CNVs and SVs.
"""

from sqlalchemy import Column, Integer, String, Text, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from base import Base


class Mutation(Base):
    """Base class for all mutations"""

    id = Column(Integer, primary_key=True)
    library_id = Column(Integer, ForeignKey("library.id"))
    mutation_type = Column(String(50))
    status = Column(Enum("somatic", "germline", "artifact", "unknown"))

    __mapper_args__ = {"polymorphic_on": mutation_type}

    library = relationship("Library", backref="mutations")


class SingleNucleotideVariant(Mutation):
    """Model for single nucleotide variants"""

    id = Column(Integer, ForeignKey("mutation.id"), primary_key=True)
    chrom = Column(String(length=50))
    pos = Column(Integer)
    ref_allele = Column(Enum("A", "T", "G", "C"))
    alt_allele = Column(Enum("A", "T", "G", "C"))
    ref_count = Column(Integer)
    alt_count = Column(Integer)

    mutation = relationship("Mutation", backref="snv")


class Indel(Mutation):
    """Model for indels"""

    id = Column(Integer, ForeignKey("mutation.id"), primary_key=True)
    chrom = Column(String(length=50))
    pos = Column(Integer)
    ref_allele = Column(Text)
    alt_allele = Column(Text)
    ref_count = Column(Integer)
    alt_count = Column(Integer)

    mutation = relationship("Mutation", backref="indel")


class StructuralVariation(Mutation):
    """Model for structural variations"""

    id = Column(Integer, ForeignKey("mutation.id"), primary_key=True)
    chrom1 = Column(String(length=50))
    pos1 = Column(Integer)
    strand1 = Column(String(length=1))
    chrom2 = Column(String(length=50))
    pos2 = Column(Integer)
    strand2 = Column(String(length=1))
    sv_type = Column(Enum("translocation", "inversion", "insertion", "deletion", "duplication"))

    mutation = relationship("Mutation", backref="sv")


class CopyNumberVariation(Mutation):
    """Model for copy number variations"""

    id = Column(Integer, ForeignKey("mutation.id"), primary_key=True)
    chrom = Column(String(length=50))
    start_pos = Column(Integer)
    end_pos = Column(Integer)
    size = Column(Integer)
    fold_change = Column(Float)
    copy_state = Column(Integer)

    mutation = relationship("Mutation", backref="cnv")
