#!/usr/bin/env python

from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from base import Base


class Gene(Base):
    """Model for gene annotations"""
    __tablename__ = "gene"

    id = Column(Integer, primary_key=True)
    ensembl_id = Column(String(length=50))
    gene_symbol = Column(String(length=50))
    biotype = Column(String(length=50))
    chr = Column(String(length=50))
    pos_start = Column(Integer)
    pos_end = Column(Integer)


class Transcript(Base):
    """Model for transcript annotations"""
    __tablename__ = "transcript"

    id = Column(Integer, primary_key=True)
    ensembl_id = Column(String(length=50))
    gene_id = Column(Integer, ForeignKey("gene.id"))
    length = Column(Integer)
    cds_start = Column(Integer)
    cds_end = Column(Integer)

class Exon(Base):
    """Model for exon annotations"""
    __tablename__ = "exon"

    id = Column(Integer, primary_key=True)
    ensembl_id = Column(String(length=50))
    gene_id = Column(Integer, ForeignKey("gene.id"))
    transcript_id = Column(Integer, ForeignKey("transcript.id"))
    transcript_start = Column(Integer)
    transcript_end = Column(Integer)
    genomic_start = Column(Integer)
    genomic_end = Column(Integer)
    strand = Column(Enum("+", "-"))
    phase = Column(Enum("-1", "0", "1", "2"))
    end_phase = Column(Enum("-1", "0", "1", "2"))


class Protein(Base):
    """Model for protein annotations"""
    __tablename__ = "protein"

    id = Column(Integer, primary_key=True)
    ensembl_id = Column(String(length=50))
    gene_id = Column(Integer, ForeignKey("gene.id"))
    transcript_id = Column(Integer, ForeignKey("transcript.id"))
    length = Column(Integer)
