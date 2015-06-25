"""
mutations.py
============
This submodule contains all classes representing mutations
in cancer, notably SNVs, indels, CNVs and SVs.
"""

from sqlalchemy import Column, Integer, String, Text, Float, Enum, ForeignKey
from sqlalchemy.orm import relationship
import base
import misc


class Mutation(base.Base):
    """Base class for all mutations"""

    id = Column(Integer, primary_key=True)
    library_id = Column(Integer, ForeignKey("library.id"))
    mutation_type = Column(String(50))
    status = Column(Enum("somatic", "germline", "artifact", "unknown"))

    __mapper_args__ = {"polymorphic_on": mutation_type}

    library = relationship("Library", backref="mutations")

    def is_overlap(self, chrom, pos1, pos2=None, margin=0):
        """Return whether given position overlaps with mutation.
        """
        raise NotImplementedError()


class SingleNucleotideVariant(Mutation):
    """Model for single nucleotide variants"""

    id = Column(Integer, ForeignKey("mutation.id"), primary_key=True)
    chrom = Column(String(length=50))
    pos = Column(Integer)
    ref_allele = Column(Enum("A", "T", "G", "C"))
    alt_allele = Column(Enum("A", "T", "G", "C"))
    ref_count = Column(Integer)
    alt_count = Column(Integer)

    __mapper_args__ = {'polymorphic_identity': 'snv'}

    mutation = relationship("Mutation", backref="snv")

    def is_overlap(self, chrom, pos1, pos2=None, margin=0):
        """Return whether given position overlaps with SNV.
        """
        snv_interval = misc.GenomicInterval(self.chrom, self.pos)
        query_interval = misc.GenomicInterval(chrom, pos1, pos2)
        return snv_interval.is_overlap(query_interval, margin)


class Indel(Mutation):
    """Model for indels"""

    id = Column(Integer, ForeignKey("mutation.id"), primary_key=True)
    chrom = Column(String(length=50))
    pos = Column(Integer)
    ref_allele = Column(Text)
    alt_allele = Column(Text)
    ref_count = Column(Integer)
    alt_count = Column(Integer)

    __mapper_args__ = {'polymorphic_identity': 'indel'}

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
    t_ref_count = Column(Integer)
    n_ref_count = Column(Integer)
    t_alt_count = Column(Integer)
    n_alt_count = Column(Integer)
    t_ref_spanning_reads = Column(Integer)
    n_ref_spanning_reads = Column(Integer)
    t_ref_read_pairs = Column(Integer)
    n_ref_read_pairs = Column(Integer)
    t_alt_spanning_reads = Column(Integer)
    n_alt_spanning_reads = Column(Integer)
    t_alt_read_pairs = Column(Integer)
    n_alt_read_pairs = Column(Integer)

    __mapper_args__ = {'polymorphic_identity': 'sv'}

    mutation = relationship("Mutation", backref="sv")

    def predict_effects(self, db_sess):
        """Predict the effect of the SV
        """
        effects = []
        # First, consider structural effects
        if self.sv_type in ["translocation", "inversion"]:
            pass
        # Second, consider copy number effects
        if self.sv_type in ["duplication", "deletion"]:
            pass
        # Return effects
        return effects

    def is_overlap(self, chrom, pos1, pos2=None, margin=0):
        """Return whether the given position overlap with
        the structural variation.
        The margin defines how close the events can be to
        be considered overlapping (e.g., within 10 bp).
        """
        query_interval = misc.GenomicInterval(chrom, pos1, pos2)
        if self.chrom1 == self.chrom2:
            sv_interval = misc.GenomicInterval(self.chrom1, self.pos1, self.pos2)
            is_overlap = sv_interval.is_overlap(query_interval, margin)
        else:
            sv_interval1 = misc.GenomicInterval(self.chrom1, self.pos1)
            sv_interval2 = misc.GenomicInterval(self.chrom2, self.pos2)
            is_overlap = (sv_interval1.is_overlap(query_interval, margin) or
                          sv_interval2.is_overlap(query_interval, margin))
        return is_overlap


class CopyNumberVariation(Mutation):
    """Model for copy number variations"""

    id = Column(Integer, ForeignKey("mutation.id"), primary_key=True)
    chrom = Column(String(length=50))
    start_pos = Column(Integer)
    end_pos = Column(Integer)
    size = Column(Integer)
    fold_change = Column(Float)
    copy_state = Column(Integer)

    __mapper_args__ = {'polymorphic_identity': 'cnv'}

    mutation = relationship("Mutation", backref="cnv")
