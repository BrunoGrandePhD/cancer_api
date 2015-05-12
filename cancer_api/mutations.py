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

    def is_overlap(self, chrom, pos1, pos2=None):
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

    def is_overlap(self, chrom, pos1, pos2=None, margin=0):
        """Return whether the given position overlap with
        the structural variation.
        The margin defines how close the events can be to
        be considered overlapping (e.g., within 10 bp).
        """
        # Ensure that pos1 < pos2
        if pos2 and not pos1 < pos2:
            pos1, pos2 = pos2, pos1
        # Check proximity to breakpoints
        is_overlap_inter = False
        breakpoints = [(self.chrom1, self.pos1), (self.chrom2, self.pos2)]
        if pos2:
            is_overlap_inter = any([sv_chrom == chrom and (sv_pos >= pos1 - margin and
                                                           sv_pos <= pos2 + margin)
                                    for sv_chrom, sv_pos in breakpoints])
        else:
            is_overlap_inter = any([sv_chrom == chrom and (sv_pos >= pos1 - margin and
                                                           sv_pos <= pos1 + margin)
                                    for sv_chrom, sv_pos in breakpoints])
        # Check overlap with intra-chromosomal events (e.g., in middle of inversion)
        is_overlap_intra = False
        if chrom == self.chrom1 and self.chrom1 == self.chrom2:
            # Ensure that sv_pos1 < sv_pos2
            sv_pos1, sv_pos2 = self.pos1, self.pos2
            if not sv_pos1 < sv_pos2:
                sv_pos1, sv_pos2 = sv_pos2, sv_pos1
            is_overlap_intra = (sv_pos1 <= pos1 + margin and sv_pos2 >= pos1 - margin)
            if pos2:
                is_overlap_intra = is_overlap_intra or (sv_pos1 <= pos2 + margin and
                                                        sv_pos2 >= pos2 - margin)
        # Return True if any are True
        return is_overlap_inter or is_overlap_intra


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
