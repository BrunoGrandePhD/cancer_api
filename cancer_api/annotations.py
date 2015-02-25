"""
annotations.py
==============
This submodule contains all classes representing reference
genome annotations, such as genes, transcripts and proteins.
"""

from sqlalchemy import Column, Integer, String, Enum, ForeignKey
from sqlalchemy.orm import relationship
from base import Base


class Gene(Base):
    """Model for gene annotations"""

    id = Column(Integer, primary_key=True)
    gene_ensembl_id = Column(String(length=50))
    gene_symbol = Column(String(length=50))
    biotype = Column(String(length=50))
    chrom = Column(String(length=50))
    start_pos = Column(Integer)
    end_pos = Column(Integer)
    length = Column(Integer)

    unique_on = ["gene_ensembl_id"]

    @classmethod
    def iter_genes_in_region(cls, session, chrom, start_pos, end_pos):
        """Iterator for genes in a given genomic region."""
        pass


class Transcript(Base):
    """Model for transcript annotations"""

    id = Column(Integer, primary_key=True)
    transcript_ensembl_id = Column(String(length=50))
    gene_id = Column(Integer, ForeignKey("gene.id"))
    cds_start_pos = Column(Integer)
    cds_end_pos = Column(Integer)
    length = Column(Integer)

    gene = relationship("Gene", backref="transcripts")

    unique_on = ["transcript_ensembl_id"]


class Exon(Base):
    """Model for exon annotations"""

    id = Column(Integer, primary_key=True)
    exon_ensembl_id = Column(String(length=50))
    gene_id = Column(Integer, ForeignKey("gene.id"))
    transcript_id = Column(Integer, ForeignKey("transcript.id"))
    transcript_start_pos = Column(Integer)
    transcript_end_pos = Column(Integer)
    genome_start_pos = Column(Integer)
    genome_end_pos = Column(Integer)
    length = Column(Integer)
    strand = Column(Enum("1", "-1"))
    phase = Column(Enum("-1", "0", "1", "2"))
    end_phase = Column(Enum("-1", "0", "1", "2"))

    gene = relationship("Gene", backref="exons")
    gene = relationship("Transcript", backref="exons")

    unique_on = ["exon_ensembl_id"]


class Protein(Base):
    """Model for protein annotations"""

    id = Column(Integer, primary_key=True)
    protein_ensembl_id = Column(String(length=50))
    gene_id = Column(Integer, ForeignKey("gene.id"))
    transcript_id = Column(Integer, ForeignKey("transcript.id"))
    cds_length = Column(Integer)

    gene = relationship("Gene", backref="proteins")
    gene = relationship("Transcript", backref="proteins")

    unique_on = ["protein_ensembl_id"]
