#!/usr/bin/env python

from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from base import Base


class Gene(Base):
    """Model for gene annotations"""
    __tablename__ = "gene"

    id = Column(Integer, primary_key=True)
    gene_ensembl_id = Column(String(length=50))
    gene_symbol = Column(String(length=50))
    biotype = Column(String(length=50))
    chrom = Column(String(length=50))
    start_pos = Column(Integer)
    end_pos = Column(Integer)
    length = Column(Integer)


class Transcript(Base):
    """Model for transcript annotations"""
    __tablename__ = "transcript"

    id = Column(Integer, primary_key=True)
    transcript_ensembl_id = Column(String(length=50))
    gene_id = Column(Integer, ForeignKey("gene.id"))
    cds_start_pos = Column(Integer)
    cds_end_pos = Column(Integer)
    length = Column(Integer)

    gene = relationship("Gene", backref="transcripts")

class Exon(Base):
    """Model for exon annotations"""
    __tablename__ = "exon"

    id = Column(Integer, primary_key=True)
    exon_ensembl_id = Column(String(length=50))
    gene_id = Column(Integer, ForeignKey("gene.id"))
    transcript_id = Column(Integer, ForeignKey("transcript.id"))
    transcript_start_pos = Column(Integer)
    transcript_end_pos = Column(Integer)
    genome_start_pos = Column(Integer)
    genome_end_pos = Column(Integer)
    length = Column(Integer)
    strand = Column(Enum("+", "-"))
    phase = Column(Enum("-1", "0", "1", "2"))
    end_phase = Column(Enum("-1", "0", "1", "2"))

    gene = relationship("Gene", backref="exons")
    gene = relationship("Transcript", backref="exons")


class Protein(Base):
    """Model for protein annotations"""
    __tablename__ = "protein"

    id = Column(Integer, primary_key=True)
    protein_ensembl_id = Column(String(length=50))
    gene_id = Column(Integer, ForeignKey("gene.id"))
    transcript_id = Column(Integer, ForeignKey("transcript.id"))
    nucl_length = Column(Integer)

    gene = relationship("Gene", backref="proteins")
    gene = relationship("Transcript", backref="proteins")
