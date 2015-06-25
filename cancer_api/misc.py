"""
misc.py
=======
This submodule contains all classes that don't belong
elsewhere for the moment. Eventually, another submodule
might be added and classes herein moved there.
"""

from base import CancerApiObject


class GenomicInterval(CancerApiObject):
    """Simple class for representing genomic intervals."""

    unique_on = ["chrom", "start_pos", "end_pos"]

    def __init__(self, chrom, start_pos, end_pos=None):
        self.chrom = str(chrom)
        self.start_pos = int(start_pos)
        if end_pos:
            self.end_pos = int(end_pos)
        else:
            self.end_pos = int(start_pos)
        # Ensure that start < end
        if not self.start_pos <= self.end_pos:
            self.start_pos, self.end_pos = self.end_pos, self.start_pos

    @property
    def length(self):
        return self.end_pos - self.start_pos + 1

    def is_overlap(self, other, margin=0):
        """Return whether two genomic intervals overlap.
        """
        # Check if on same chromosome
        if self.chrom != other.chrom:
            return False

        # Define function to check is position is in range
        def is_intra(range_start, range_end, query_pos, margin):
            """Check if point is within a given range
            """
            is_intra = (range_start - margin <= query_pos and
                        query_pos <= range_end + margin)
            return is_intra

        # Check for each region edge (start_pos and end_pos) reciprocally
        def is_overlap_oneway(self, other):
            """Returns whether one genomic region overlaps another (one way).
            It does so by check whether either edge of the `other` region is "intra".
            """
            is_overlap_oneway = (
                is_intra(self.start_pos, self.end_pos, other.start_pos, margin) or
                is_intra(self.start_pos, self.end_pos, other.end_pos, margin))
            return is_overlap_oneway

        # Check overlap both ways
        is_overlap_bothways = (is_overlap_oneway(self, other) or is_overlap_oneway(other, self))
        return is_overlap_bothways


class RawRead(CancerApiObject):
    """Simple class for representing raw sequence reads"""

    unique_on = ["id", "seq", "strand", "qual"]

    def __init__(self, id, seq, strand, qual):
        self.id = id
        self.seq = seq
        self.strand = strand
        self.qual = qual
