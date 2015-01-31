#!/usr/bin/env python

from sqlalchemy import Column, Integer, String, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
from base import Base


class Mutation(Base):
    """Base class for all mutations"""
    __tablename__ = "mutation"

    id = Column(Integer, primary_key=True)
    library_id = Column(Integer, ForeignKey("library.id"))
    mutation_type = Column(String(50))
    status = Column(Enum("somatic", "germline", "artifact", "unknown"))

    __mapper_args__ = {"polymorphic_on": mutation_type}

    library = relationship("Library", backref="mutations")


class SingleNucleotideVariant(Mutation):
    """Model for single nucleotide variants
    (i.e. involving one genomic position)
    """
    __tablename__ = "snv"

    id = Column(Integer, ForeignKey("mutation.id"), primary_key=True)
    chrom = Column(String(length=50))
    pos = Column(Integer)
    ref_allele = Column(String(length=1))
    alt_allele = Column(String(length=1))
    ref_count = Column(Integer)
    alt_count = Column(Integer)


class StructuralVariation(Mutation):
    """Model for structural variations"""
    __tablename__ = "sv"

    id = Column(Integer, ForeignKey("mutation.id"), primary_key=True)
    chrom1 = Column(String(length=50))
    pos1 = Column(Integer)
    strand1 = Column(String(length=1))
    chrom2 = Column(String(length=50))
    pos2 = Column(Integer)
    strand2 = Column(String(length=1))
    sv_type = Column(Enum("translocation", "inversion", "insertion", "deletion", "duplication"))


class CopyNumberVariation(Mutation):
    """Model for copy number variations as called by
    callers which provide a fold-change
    (e.g. like tools which use read depth)
    """
    __tablename__ = "cnv"

    id = Column(Integer, ForeignKey("mutation.id"), primary_key=True)
    chrom = Column(String(length=50))
    start_pos = Column(Integer)
    end_pos = Column(Integer)
    size = Column(Integer)
    fold_change = Column(Float)
    copy_state = Column(Integer)
